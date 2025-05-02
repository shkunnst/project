import logging
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from attempt import attempt_connection
import json
from storage import boostrap_servers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_messages():
    logger.info("Try to connect %s", boostrap_servers)
    consumer = AIOKafkaConsumer('user_requests', bootstrap_servers=boostrap_servers, group_id="user-group")
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

    await attempt_connection(consumer=consumer, producer=producer)

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            logger.info("User Service received: %s", data)
            if "login" not in data or "password" not in data:
                await producer.send_and_wait("auth_responses", json.dumps({"request_id": data.get("request_id"), "error": "Missing login or password"}).encode())
            else:
                logger.info("Sent request to auth_requests: %s", data)
                await producer.send_and_wait("auth_requests", json.dumps(data).encode())
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())
