from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.rbac import require_lawyer
from backend.db.database import get_db
from backend.schemas.base import APIResponse
from backend.schemas.escalation import (
    EscalationQueueResponse,
    ReviewEscalationRequest,
    ReviewEscalationResponse,
)
from backend.services.escalation_service import EscalationService

router = APIRouter()


@router.get("/", response_model=APIResponse[EscalationQueueResponse])
async def get_escalations(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_lawyer),
):
    service = EscalationService(db)
    result = await service.get_queue()
    return APIResponse(success=True, data=result)


@router.put("/{case_id}/review", response_model=APIResponse[ReviewEscalationResponse])
async def review_escalation(
    case_id: str,
    request: ReviewEscalationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_lawyer),
):
    service = EscalationService(db)
    result = await service.review(
        escalation_id=case_id,
        lawyer_id=user["sub"],
        resolution=request.resolution,
        edited_clauses=request.edited_clauses,
        lawyer_notes=request.lawyer_notes,
        approved_for_writeup=request.approved_for_writeup,
    )
    return APIResponse(success=True, data=result)
