from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.rbac import require_citizen
from backend.db.database import get_db
from backend.schemas.base import APIResponse
from backend.schemas.payment import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from backend.services.payment_service import PaymentService

router = APIRouter()


@router.post("/create-order", response_model=APIResponse[CreateOrderResponse])
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_citizen),
):
    service = PaymentService(db)
    result = await service.create_order(
        user_id=user["sub"],
        payment_type=request.payment_type,
        query_id=request.query_id,
    )
    return APIResponse(success=True, data=result)


@router.post("/verify", response_model=APIResponse[VerifyPaymentResponse])
async def verify_payment(
    request: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_citizen),
):
    service = PaymentService(db)
    result = await service.verify(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature,
    )
    return APIResponse(success=True, data=result)
