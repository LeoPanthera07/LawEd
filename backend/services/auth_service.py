import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from backend.models.user import User
from backend.models.session import Session
from backend.schemas.auth import LoginResponse, RegisterResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        email: str,
        full_name: str,
        password: str,
        phone: Optional[str] = None,
    ) -> RegisterResponse:
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise EmailAlreadyExistsError()

        user = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            phone=phone,
            role="citizen",
            is_verified=True,  # Skip email verification for MVP
            email_verification_token=secrets.token_urlsafe(32),
            email_verification_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return RegisterResponse(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
            message="Registration successful",
        )

    async def login(self, email: str, password: str) -> tuple[LoginResponse, str]:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        session = Session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.db.add(session)

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()

        login_response = LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            role=user.role,
        )
        return login_response, refresh_token
