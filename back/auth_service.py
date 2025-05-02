import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
import jwt

from attempt import attempt_connection
from storage import boostrap_servers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "mysecret"
USERS_DB = {
    "user1": "password123"
}

async def process_messages():
    consumer = AIOKafkaConsumer('auth_requests', bootstrap_servers=boostrap_servers, group_id="auth-group")
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

    await attempt_connection(consumer=consumer, producer=producer)

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            logger.info("Auth Service received: %s", data)

            request_id = data["request_id"]

            if USERS_DB.get(data["login"]) == data["password"]:
                token = jwt.encode({"user": data["login"]}, SECRET_KEY, algorithm="HS256")
                response = {"request_id": request_id, "token": token}
            else:
                response = {"request_id": request_id, "error": "Invalid credentials"}

            await producer.send_and_wait("auth_responses", json.dumps(response).encode())
            logger.info("Sent response: %s", response)
    
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())