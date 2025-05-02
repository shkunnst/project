import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from attempt import attempt_connection
from storage import boostrap_servers
from database import get_db_session, User, Department, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "mysecret"  # Should be moved to environment variables in production
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(session: AsyncSession, username: str, password: str):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def create_user(session: AsyncSession, username: str, password: str, department_id: int, 
                     recovery_word: str, recovery_hint: str, role: UserRole):
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        department_id=department_id,
        recovery_word=recovery_word,
        recovery_hint=recovery_hint,
        role=role
    )
    session.add(user)
    await session.commit()
    return user

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
                        token = jwt.encode(
                            {
                                "user": user.username,
                                "role": user.role,
                                "department_id": user.department_id
                            }, 
                            SECRET_KEY, 
                            algorithm="HS256"
                        )
                        response = {"request_id": request_id, "token": token}
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
                        response = {"request_id": request_id, "message": "User registered successfully"}
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