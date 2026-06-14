from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.security import verify_token

security = HTTPBearer()


class RBACGuard:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict:
        token = credentials.credentials
        try:
            payload = verify_token(token, "access")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
            )

        user_role = payload.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"This action requires one of: {self.allowed_roles}",
                },
            )

        return payload


require_citizen = RBACGuard(["citizen", "lawyer", "admin"])
require_lawyer = RBACGuard(["lawyer", "admin"])
require_admin = RBACGuard(["admin"])
