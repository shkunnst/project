from typing import Optional

from pydantic import BaseModel


# Pydantic models for request validation
class LoginRequest(BaseModel):
    login: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    recovery_word: str
    recovery_hint: str


class PasswordRecoveryRequest(BaseModel):
    username: str
    recovery_word: str
    new_password: str


class RecoveryHintRequest(BaseModel):
    username: str


class WorkDataUpdate(BaseModel):
    working_hours: Optional[float] = None
    bonuses: Optional[float] = None
    fines: Optional[float] = None


class WorkDataResponse(BaseModel):
    user_id: int
    working_hours: float
    bonuses: float
    fines: float
