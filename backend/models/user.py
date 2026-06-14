import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="citizen"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(255))
    email_verification_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_reset_token: Mapped[str | None] = mapped_column(String(255))
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bar_council_id: Mapped[str | None] = mapped_column(String(100))
    free_queries_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    free_queries_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("role IN ('citizen', 'lawyer', 'admin')", name="check_user_role"),
    )
