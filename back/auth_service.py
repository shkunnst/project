import asyncio
import json
import jwt
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select
from datetime import datetime, timedelta

from attempt import attempt_connection
from back.services.auth import (
    authenticate_user,
    get_password_hash,
    create_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_DAYS
)
from back.settings import SECRET_KEY, logger
from database import get_db_session, User, UserRole
from storage import boostrap_servers


async def process_messages():
    consumer = AIOKafkaConsumer('auth_requests', bootstrap_servers=boostrap_servers, group_id="auth-group")
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

    await attempt_connection(consumer=consumer, producer=producer)

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            logger.info("Auth Service received: %s", data)

            request_id = data["request_id"]
            action = data.get("action", "login")
            session = await get_db_session()

            try:
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
                    try:
                        user = await create_user(
                            session=session,
                            username=data["username"],
                            password=data["password"],
                            department_id=data["department_id"],
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
                await session.close()

            await producer.send_and_wait("auth_responses", json.dumps(response).encode())
            logger.info("Sent response: %s", response)

    finally:
        await consumer.stop()
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(process_messages())
