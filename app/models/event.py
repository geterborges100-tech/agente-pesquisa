from __future__ import annotations
import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class EventStatus(str, enum.Enum):
    RECEIVED  = "received"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    FAILED    = "failed"

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_event_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[EventStatus] = mapped_column(String(32), nullable=False, default=EventStatus.RECEIVED)
    sender_phone: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    payload_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_webhook_events_status_received", "status", "received_at"),
    )

    def __repr__(self) -> str:
        return f"<WebhookEvent id={self.id} external={self.external_event_id!r} status={self.status}>"
