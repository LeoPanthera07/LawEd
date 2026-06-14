import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_language: Mapped[str | None] = mapped_column(String(20))
    translated_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    pipeline_run_id: Mapped[str | None] = mapped_column(String(255))
    pipeline_error: Mapped[str | None] = mapped_column(Text)
    is_guest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_duration_ms: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'escalated', 'failed')",
            name="check_query_status",
        ),
    )
