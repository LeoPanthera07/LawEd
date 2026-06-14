import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    query_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id")
    )
    razorpay_order_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    razorpay_signature: Mapped[str | None] = mapped_column(String(500))
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    payment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    failure_reason: Mapped[str | None] = mapped_column(Text)
    webhook_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("amount_paise > 0", name="check_payment_amount"),
        CheckConstraint(
            "payment_type IN ('query', 'writeup', 'subscription')",
            name="check_payment_type",
        ),
        CheckConstraint(
            "status IN ('created', 'paid', 'failed', 'refunded')",
            name="check_payment_status",
        ),
    )
