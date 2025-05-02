from pydantic import BaseModel


# Pydantic models for request validation
class LoginRequest(BaseModel):
    login: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    department_id: int
    recovery_word: str
    recovery_hint: str
    role: str

class PasswordRecoveryRequest(BaseModel):
    username: str
    recovery_word: str
    new_password: str