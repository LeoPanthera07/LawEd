from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from backend.schemas.base import APIResponse
from backend.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=APIResponse[RegisterResponse], status_code=201)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.register(
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        phone=request.phone,
    )
    return APIResponse(success=True, data=result)


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result, refresh_token = await service.login(
        email=request.email,
        password=request.password,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return APIResponse(success=True, data=result)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return APIResponse(success=True, data={"message": "Logged out"})
