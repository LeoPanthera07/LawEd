import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Writeup(Base):
    __tablename__ = "writeups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id"), nullable=False
    )
    clause_map_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clause_maps.id"), nullable=False
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payments.id"), unique=True, nullable=False
    )
    citizen_name: Mapped[str] = mapped_column(String(255), nullable=False)
    citizen_contact: Mapped[str] = mapped_column(String(100), nullable=False)
    incident_date: Mapped[Optional[datetime]] = mapped_column(Date)
    incident_summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(String(50))
    pdf_path: Mapped[str | None] = mapped_column(String(500))
    pdf_size_bytes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    generation_error: Mapped[str | None] = mapped_column(Text)
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    generation_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "recommended_action IN ('file_fir', 'approach_lawyer', 'file_complaint') OR recommended_action IS NULL",
            name="check_writeup_action",
        ),
        CheckConstraint(
            "status IN ('pending', 'generating', 'ready', 'failed')",
            name="check_writeup_status",
        ),
    )
