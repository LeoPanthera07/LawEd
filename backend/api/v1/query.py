from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.rbac import require_citizen
from backend.db.database import get_db
from backend.schemas.base import APIResponse
from backend.schemas.query import (
    QueryResultResponse,
    QuerySubmitRequest,
    QuerySubmitResponse,
)
from backend.services.query_service import QueryService

router = APIRouter()


@router.post("/submit", response_model=APIResponse[QuerySubmitResponse], status_code=202)
async def submit_query(
    request: QuerySubmitRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_citizen),
):
    service = QueryService(db)
    result = await service.submit(
        user_id=user["sub"],
        input_text=request.input_text,
        is_guest=request.is_guest,
        ip_address=req.client.host if req.client else None,
        background_tasks=background_tasks,
    )
    return APIResponse(success=True, data=result)


@router.get("/{query_id}", response_model=APIResponse[QueryResultResponse])
async def get_query_result(
    query_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_citizen),
):
    service = QueryService(db)
    result = await service.get_result(query_id=query_id, user_id=user["sub"])
    return APIResponse(success=True, data=result)
