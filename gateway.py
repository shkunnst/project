from fastapi import FastAPI
from aiokafka import AIOKafkaProducer
import asyncio
import json
import uuid

from attempt import attempt_connection
from storage import boostrap_servers

app = FastAPI()

producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)

@app.on_event("startup")
async def start_producer():
    await attempt_connection(producer=producer)

@app.on_event("shutdown")
async def stop_producer():
    await producer.stop()

@app.post("/login")
async def login(data: dict):
    request_id = str(uuid.uuid4())
    data["request_id"] = request_id

    await producer.send_and_wait("user_requests", json.dumps(data).encode())

    return {"request_id": request_id, "status": "processing"}

