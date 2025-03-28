import logging
from fastapi import FastAPI
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import uuid

from attempt import attempt_connection
from storage import boostrap_servers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

producer = None
consumer = None
pending_requests = {}

@app.on_event("startup")
async def startup_event():
    global producer
    global consumer
    logger.info("Try to connect %s", boostrap_servers)
    producer = AIOKafkaProducer(bootstrap_servers=boostrap_servers)
    consumer = AIOKafkaConsumer('auth_responses', bootstrap_servers=boostrap_servers, group_id="gateway-group")
    await attempt_connection(producer=producer, consumer=consumer)
    # asyncio.create_task(process_responses())

@app.on_event("shutdown")
async def shutdown_event():
    if producer:
        await producer.stop()
        await consumer.stop()

@app.post("/login")
async def login(data: dict):
    request_id = str(uuid.uuid4())
    data["request_id"] = request_id

    # Store the request in the pending_requests dictionary
    pending_requests[request_id] = data

    await producer.send_and_wait("user_requests", json.dumps(data).encode())
    logger.info("Sent request to Kafka for authentication: %s", data)

    try:
        async for msg in consumer:
            response = json.loads(msg.value.decode())
            request_id = response.get("request_id")

            if request_id in pending_requests:
                # Retrieve the original request
                original_request = pending_requests.pop(request_id)
                # Here you can send the response back to the client
                logger.info("Received response for request_id: %s, response: %s", request_id, response)
                return response
            else:
                logger.info("No response received for request_id: %s", request_id)
                # Here you can handle the case when no response is received within a certain timeframe
                # You can also send a timeout error to the client
    except Exception as e:
        logger.error(f"Error processing response from Kafka {e}")
        # Here you can handle the error, for example, retry the request or send a notification to the client


    # return {"request_id": request_id, "status": "processing"}

# async def process_responses():
#     consumer = AIOKafkaConsumer('auth_responses', bootstrap_servers=boostrap_servers, group_id="gateway-group")
#     await attempt_connection(consumer=consumer)
#
#     try:
#         async for msg in consumer:
#             response = json.loads(msg.value.decode())
#             request_id = response.get("request_id")
#
#             if request_id in pending_requests:
#                 # Retrieve the original request
#                 original_request = pending_requests.pop(request_id)
#                 # Here you can send the response back to the client
#                 logger.info("Received response for request_id: %s, response: %s", request_id, response)
#                 with open("/app/logs/responses.txt", "a") as file:
#                     file.write(f"Response for request_id: {request_id}, \n request: {original_request}: {response}\n")
#
#     finally:
#         await consumer.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)