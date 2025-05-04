from typing import Optional

from pydantic import BaseModel

from back.models import UserRole


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
    username: str  # Added username field
    working_hours: float
    bonuses: float
    fines: float


class UserAdminUpdate(BaseModel):
    username: str  # Added username field
    working_hours: float
    bonuses: float
    fines: float
    role: UserRole
    department_id: Optional[int]
