from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
import jwt

SECRET_KEY = "mysecret"
USERS_DB = {
    "user1": "password123"
}

async def process_messages():
    consumer = AIOKafkaConsumer('auth_requests', bootstrap_servers='localhost:9092', group_id="auth-group")
    producer = AIOKafkaProducer(bootstrap_servers='localhost:9092')

    await consumer.start()
    await producer.start()
    
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode())
            print("Auth Service received:", data)

            request_id = data["request_id"]
            response = {}

            if USERS_DB.get(data["login"]) == data["password"]:
                token = jwt.encode({"user": data["login"]}, SECRET_KEY, algorithm="HS256")
                response = {"request_id": request_id, "token": token}
            else:
                response = {"request_id": request_id, "error": "Invalid credentials"}

            await producer.send_and_wait("auth_responses", json.dumps(response).encode())
    
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())

