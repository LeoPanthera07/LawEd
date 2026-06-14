from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.rbac import require_admin
from backend.db.database import get_db
from backend.schemas.base import APIResponse

router = APIRouter()


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    return APIResponse(success=True, data={"message": "Admin users endpoint"})


@router.put("/users/{user_id}/role")
async def assign_role(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    return APIResponse(success=True, data={"message": "Role assignment endpoint"})


@router.get("/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    return APIResponse(success=True, data={"message": "Analytics endpoint"})
