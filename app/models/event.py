"""
app/models/event.py
Tabela de log de eventos recebidos via Webhook (idempotência).

Usa o mesmo Base de models_v1.py — importe de lá em produção:
    from app.models.base import Base
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ---------------------------------------------------------------------------
# Em produção: substitua por `from app.models.base import Base`
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class EventStatus(str, enum.Enum):
    RECEIVED  = "received"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    FAILED    = "failed"


class WebhookEvent(Base):
    """
    Persiste cada evento recebido do webhook da Meta.

    * ``external_event_id`` → ID único fornecido pela Meta (campo ``id`` da mensagem).
    * ``status``            → ciclo de vida do processamento.
    * ``payload_raw``       → JSON bruto para auditoria / reprocessamento.
    """

    __tablename__ = "webhook_events"

    # PK inteiro — tabela de log, sem necessidade de UUID público.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identificador externo da Meta (ex.: wamid.xxx)
    external_event_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="ID único do evento fornecido pela Meta",
    )

    # Tipo de evento: "message", "status", "reaction", etc.
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus),
        nullable=False,
        default=EventStatus.RECEIVED,
        server_default=EventStatus.RECEIVED.value,
    )

    # Número E.164 sem "+" — referência rápida sem FK obrigatória
    sender_phone: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)

    # UUID do Contact resolvido após upsert (nullable até resolução)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Payload completo para auditoria / reprocessamento
    payload_raw: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Mensagem de erro caso status == FAILED
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ------------------------------------------------------------------
    # Índices compostos
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_webhook_events_status_received", "status", "received_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<WebhookEvent id={self.id} external={self.external_event_id!r}"
            f" status={self.status}>"
        )
