import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.payment import CreateOrderResponse, VerifyPaymentResponse
from backend.models.payment import Payment


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        user_id: str,
        payment_type: str,
        query_id: Optional[str] = None,
    ) -> CreateOrderResponse:
        amount_paise = 2900 if payment_type == "query" else 9900

        payment = Payment(
            user_id=uuid.UUID(user_id),
            query_id=uuid.UUID(query_id) if query_id else None,
            razorpay_order_id=f"order_{uuid.uuid4().hex[:16]}",
            amount_paise=amount_paise,
            payment_type=payment_type,
            status="created",
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        return CreateOrderResponse(
            razorpay_order_id=payment.razorpay_order_id,
            amount_paise=payment.amount_paise,
            currency="INR",
            payment_id=str(payment.id),
        )

    async def verify(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> VerifyPaymentResponse:
        from sqlalchemy import select
        from backend.core.exceptions import PaymentVerificationError

        result = await self.db.execute(
            select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise PaymentVerificationError()

        # TODO: Verify Razorpay signature in production
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "paid"
        payment.paid_at = datetime.now(timezone.utc)
        await self.db.commit()

        return VerifyPaymentResponse(
            payment_id=str(payment.id),
            status="paid",
            amount_paise=payment.amount_paise,
        )
