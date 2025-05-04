import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from attempt import attempt_connection
from back.models import User, UserRole
from back.services.auth import (
    authenticate_user,
    get_password_hash,
    create_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_DAYS
)
from back.settings import logger
from database import get_async_db
from storage import boostrap_servers

router = APIRouter()

@router.get("/recovery-hint", response_model=dict)
async def get_recovery_hint(
    username: str = Query(..., description="Username to get recovery hint for"),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Get the recovery hint for a user to help them remember their recovery word.
    This endpoint is used in the password recovery process.
    """
    # Find the user by username
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user:
        # For security reasons, don't reveal whether a username exists or not
        # Just return a generic message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return the recovery hint
    return {"recovery_hint": user.recovery_hint}

async def process_messages():
    consumer = AIOKafkaConsumer('auth_requests', bootstrap_servers=boostrap_servers, group_id="auth-group")
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

    await attempt_connection(consumer=consumer, producer=producer)
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            request_id = data["request_id"]
            action = data.get("action", "login")
            session = None
            try:
                async for session in get_async_db():

                    if action == "login":
                        user = await authenticate_user(session, data["login"], data["password"])
                        if user:
                            token = create_access_token({"sub": user.username})
                            response = {
                                "request_id": request_id,
                                "token": token,
                                "expires_in": ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
                            }
                        else:
                            response = {"request_id": request_id, "error": "Invalid credentials"}

                    elif action == "register":
                        logger.info("Received request to register: %s", data)
                        try:
                            user = await create_user(
                                session=session,
                                username=data["username"],
                                password=data["password"],
                                recovery_word=data["recovery_word"],
                                recovery_hint=data["recovery_hint"],
                                role=UserRole(data["role"])
                            )
                            token = create_access_token({"sub": user.username})
                            response = {
                                "request_id": request_id,
                                "message": "User registered successfully",
                                "token": token,
                                "expires_in": ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
                            }
                        except Exception as e:
                            response = {"request_id": request_id, "error": str(e)}

                    elif action == "recover_password":
                        result = await session.execute(
                            select(User).where(
                                User.username == data["username"],
                                User.recovery_word == data["recovery_word"]
                            )
                        )
                        user = result.scalar_one_or_none()
                        if user:
                            new_password = get_password_hash(data["new_password"])
                            user.password = new_password
                            await session.commit()
                            response = {"request_id": request_id, "message": "Password updated successfully"}
                        else:
                            response = {"request_id": request_id, "error": "Invalid recovery information"}

                    else:
                        response = {"request_id": request_id, "error": "Invalid action"}

            except Exception as e:
                response = {"request_id": request_id, "error": str(e)}
            finally:
                if session:
                    await session.close()

            await producer.send_and_wait("auth_responses", json.dumps(response).encode())
            logger.info("Sent response: %s", response)

    finally:
        await consumer.stop()
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(process_messages())
