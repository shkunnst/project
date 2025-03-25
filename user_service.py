from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json

from attempt import attempt_connection
from storage import boostrap_servers


async def process_messages():
    print("Try to connect ", boostrap_servers)
    consumer = AIOKafkaConsumer('user_requests', bootstrap_servers=boostrap_servers, group_id="user-group")
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

    await attempt_connection(consumer=consumer, producer=producer)

    
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            print("User Service received:", data)

            if "login" not in data or "password" not in data:
                continue

            request_id = data.get("request_id")
            response = {"request_id": request_id, "status": "ok"}

            await producer.send_and_wait("auth_responses", json.dumps(response).encode())
    
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())

