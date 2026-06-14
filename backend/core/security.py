from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.config import settings
from backend.core.exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": TokenType.ACCESS,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": TokenType.REFRESH,
        "iat": now,
        "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm="HS256")


def verify_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise JWTError("Wrong token type")
        return payload
    except JWTError as e:
        raise InvalidTokenError(str(e))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
