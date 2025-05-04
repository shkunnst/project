import asyncio
import json
import uuid
from typing import Dict, Any

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI, HTTPException, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from attempt import attempt_connection
from back.auth_service import router as auth_router
from back.database import get_db_session, get_async_db
from back.models import UserRole, User, Department
from back.schemas import LoginRequest, RegisterRequest, PasswordRecoveryRequest, WorkDataResponse, WorkDataUpdate
from back.services.auth import set_auth_cookie, remove_auth_cookie, get_current_user
from back.services.seed import init_db, seed
from back.services.work_data import get_user_work_data, update_user_work_data, get_department_work_data
from back.settings import logger
from storage import boostrap_servers
from sqlalchemy import select

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Work data schemas


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
        await pending_requests.pop(request_id, None)
        raise HTTPException(status_code=504, detail="Request timeout")


@app.post("/api/login")
async def login(request: LoginRequest, response: Response):
    data = {
        "action": "login",
        "login": request.login,
        "password": request.password
    }
    result = await send_kafka_request(data)
    if "token" in result:
        set_auth_cookie(response, result["token"])
    return result


@app.post("/api/register")
async def register(request: RegisterRequest, response: Response):
    data = {
        "action": "register",
        "username": request.username,
        "password": request.password,
        "recovery_word": request.recovery_word,
        "recovery_hint": request.recovery_hint,
        "role": UserRole.SUBORDINATE
    }
    result = await send_kafka_request(data)
    if "token" in result:
        set_auth_cookie(response, result["token"])
    return result


@app.post("/api/recover-password")
async def recover_password(request: PasswordRecoveryRequest):
    data = {
        "action": "recover_password",
        "username": request.username,
        "recovery_word": request.recovery_word,
        "new_password": request.new_password
    }
    return await send_kafka_request(data)


@app.post("/api/logout")
async def logout(response: Response):
    remove_auth_cookie(response)
    return {"message": "Successfully logged out"}


@app.get("/api/me")
async def get_me(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db)
):
    # Fetch department name if user has a department_id
    department_name = None
    if current_user.department_id:
        result = await session.execute(
            select(Department.name).where(Department.id == current_user.department_id)
        )
        department_name = result.scalar_one_or_none()
    
    return {
        "username": current_user.username,
        "role": current_user.role,
        "department_id": current_user.department_id,
        "department_name": department_name
    }


# Work data endpoints
@app.get("/api/work-data/{user_id}", response_model=WorkDataResponse)
async def get_work_data(user_id: int, current_user=Depends(get_current_user)):
    work_data = await get_user_work_data(user_id, current_user)
    return work_data


@app.put("/api/work-data/{user_id}", response_model=WorkDataResponse)
async def update_work_data(
        user_id: int,
        update_data: WorkDataUpdate,
        current_user=Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),

):
    work_data = await update_user_work_data(
        user_id,
        session=session,
        working_hours=update_data.working_hours,
        bonuses=update_data.bonuses,
        fines=update_data.fines,
        current_user=current_user
    )
    return work_data


@app.get("/api/department/work-data", response_model=list[WorkDataResponse])
async def get_department_work_data_endpoint(
        current_user=Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    # This will now create work data for users who don't have it
    work_data_list = await get_department_work_data(current_user, session=session)
    return work_data_list


async def main():
    # pass
    await init_db()
    await seed()


if __name__ == "__main__":
    import uvicorn

    asyncio.run(main())
    uvicorn.run("gateway:app", host="0.0.0.0", port=8000, reload=True)
