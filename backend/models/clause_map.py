import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class ClauseMap(Base):
    __tablename__ = "clause_maps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    clauses: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    acts_covered: Mapped[list | None] = mapped_column(ARRAY(String))
    clause_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_lawyer_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lawyer_reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    lawyer_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
