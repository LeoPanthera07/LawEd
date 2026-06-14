import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id"), nullable=False
    )
    clause_map_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clause_maps.id")
    )
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    high_stakes_flag: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    assigned_lawyer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lawyer_notes: Mapped[str | None] = mapped_column(Text)
    resolution: Mapped[str | None] = mapped_column(String(50))
    approved_for_writeup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    citizen_notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "reason IN ('low_confidence', 'high_stakes', 'manual')",
            name="check_escalation_reason",
        ),
        CheckConstraint(
            "status IN ('pending', 'under_review', 'resolved', 'flagged')",
            name="check_escalation_status",
        ),
        CheckConstraint(
            "resolution IN ('approved', 'edited', 'flagged') OR resolution IS NULL",
            name="check_escalation_resolution",
        ),
    )
