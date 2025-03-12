from aiokafka import AIOKafkaConsumer # type: ignore
import asyncio
import json

async def process_messages():
    consumer = AIOKafkaConsumer('auth_responses', bootstrap_servers='localhost:9092', group_id="gateway-group")
    
    await consumer.start()
    
    try:
        async for msg in consumer:
            response = json.loads(msg.value.decode())
            print("Response to client:", response)
    
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())

