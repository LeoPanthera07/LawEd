from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.rbac import require_citizen
from backend.db.database import get_db
from backend.schemas.base import APIResponse
from backend.schemas.writeup import GenerateWriteupRequest, GenerateWriteupResponse
from backend.services.writeup_service import WriteupService

router = APIRouter()


@router.post("/generate", response_model=APIResponse[GenerateWriteupResponse])
async def generate_writeup(
    request: GenerateWriteupRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_citizen),
):
    service = WriteupService(db)
    result = await service.generate(
        query_id=request.query_id,
        payment_id=request.payment_id,
        citizen_name=request.citizen_name,
        citizen_contact=request.citizen_contact,
        incident_date=request.incident_date,
        user_id=user["sub"],
    )
    return APIResponse(success=True, data=result)
