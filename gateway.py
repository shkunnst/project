from fastapi import FastAPI
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import uuid

from attempt import attempt_connection
from storage import boostrap_servers

app = FastAPI()

producer = None
pending_requests = {}

@app.on_event("startup")
async def startup_event():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)
    await attempt_connection(producer=producer)
    asyncio.create_task(process_responses())

@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@app.post("/login")
async def login(data: dict):
    request_id = str(uuid.uuid4())
    data["request_id"] = request_id

    # Store the request in the pending_requests dictionary
    pending_requests[request_id] = data

    await producer.send_and_wait("user_requests", json.dumps(data).encode())
    print("Sent request to Kafka for authentication")

    return {"request_id": request_id, "status": "processing"}

async def process_responses():
    consumer = AIOKafkaConsumer('auth_responses', bootstrap_servers=boostrap_servers, group_id="gateway-group")
    await attempt_connection(consumer=consumer)

    try:
        async for msg in consumer:
            response = json.loads(msg.value.decode())
            request_id = response.get("request_id")

            if request_id in pending_requests:
                # Retrieve the original request
                original_request = pending_requests.pop(request_id)
                # Here you can send the response back to the client
                print(f"Response for request {request_id}: {response}")

    finally:
        await consumer.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
