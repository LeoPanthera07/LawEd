from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    role: str
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
