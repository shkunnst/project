import logging
from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import uuid
from typing import Dict, Any

from starlette.middleware.cors import CORSMiddleware

from attempt import attempt_connection
from back.database import init_db, seed
from back.schemas import LoginRequest, RegisterRequest, PasswordRecoveryRequest
from storage import boostrap_servers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

producer = None
consumer = None
pending_requests: Dict[str, asyncio.Future] = {}



@app.on_event("startup")
async def startup_event():
    global producer
    global consumer
    logger.info("Try to connect %s", boostrap_servers)
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)
    consumer = AIOKafkaConsumer('auth_responses', bootstrap_servers=boostrap_servers, group_id="gateway-group")
    await attempt_connection(producer=producer, consumer=consumer)
    asyncio.create_task(process_responses())

@app.on_event("shutdown")
async def shutdown_event():
    if producer:
        await producer.stop()
        await consumer.stop()

async def process_responses():
    try:
        async for msg in consumer:
            response = json.loads(msg.value.decode())
            request_id = response.get("request_id")
            
            if request_id in pending_requests:
                future = pending_requests.pop(request_id)
                if not future.done():
                    if "error" in response:
                        future.set_exception(HTTPException(status_code=400, detail=response["error"]))
                    else:
                        future.set_result(response)
    except Exception as e:
        logger.error(f"Error processing response from Kafka: {e}")

async def send_kafka_request(data: Dict[str, Any]) -> Dict[str, Any]:
    request_id = str(uuid.uuid4())
    data["request_id"] = request_id
    
    future = asyncio.Future()
    pending_requests[request_id] = future
    
    await producer.send_and_wait("auth_requests", json.dumps(data).encode())
    logger.info("Sent request to Kafka: %s", data)
    
    try:
        return await asyncio.wait_for(future, timeout=30.0)
    except asyncio.TimeoutError:
        pending_requests.pop(request_id, None)
        raise HTTPException(status_code=504, detail="Request timeout")

@app.post("/api/login")
async def login(request: LoginRequest):
    data = {
        "action": "login",
        "login": request.login,
        "password": request.password
    }
    return await send_kafka_request(data)

@app.post("/api/register")
async def register(request: RegisterRequest):
    data = {
        "action": "register",
        "username": request.username,
        "password": request.password,
        "department_id": request.department_id,
        "recovery_word": request.recovery_word,
        "recovery_hint": request.recovery_hint,
        "role": request.role
    }
    return await send_kafka_request(data)

@app.post("/api/recover-password")
async def recover_password(request: PasswordRecoveryRequest):
    data = {
        "action": "recover_password",
        "username": request.username,
        "recovery_word": request.recovery_word,
        "new_password": request.new_password
    }
    return await send_kafka_request(data)

async def main():
    await init_db()
    await seed()


if __name__ == "__main__":
    import uvicorn
    asyncio.run(main())
    uvicorn.run(app, host="0.0.0.0", port=8000)