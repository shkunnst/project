import asyncio
import json

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


async def attempt_connection(consumer: AIOKafkaConsumer = None, producer: AIOKafkaProducer = None) -> bool:
    max_retries = 30
    retry_delay = 15

    for attempt in range(max_retries):
        try:
            if consumer is not None:
                await consumer.start()
            if producer is not None:
                await producer.start()
            break
        except Exception as e:
            print(f"Producer connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")
                raise Exception("Failed to connect to Kafka")