from __future__ import annotations

import uuid
from typing import Any
from zoneinfo import ZoneInfo          # Python 3.9+ — sem dependências externas
from datetime import datetime

from sqlalchemy.orm import Session
from app.models.models_v1 import AuditLog

# Fuso horário oficial do projeto
TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")


def _now_brasilia() -> datetime:
    """
    Retorna o datetime atual com timezone de Brasília/DF (UTC-3 ou UTC-2 no horário de verão).
    TIMESTAMPTZ no PostgreSQL armazena internamente em UTC e converte corretamente.
    """
    return datetime.now(TZ_BRASILIA)


def log_event(
    db: Session,
    *,
    event: str,
    actor: str,
    entity: str,
    entity_id: uuid.UUID,
    action: str,
    criticality: str = "medium",
    conversation_id: uuid.UUID | None = None,
    context: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Registra um evento de auditoria com timestamp em horário de Brasília/DF.

    O campo created_at é definido explicitamente em Python (não pelo server_default)
    para garantir que o offset correto de Brasília seja gravado no TIMESTAMPTZ.
    """
    row = AuditLog(
        event=event,
        actor=actor,
        entity=entity,
        entity_id=entity_id,
        action=action,
        criticality=criticality,
        conversation_id=conversation_id,
        context=context,
        created_at=_now_brasilia(),    # ← Brasília/DF explícito
    )
    db.add(row)
    db.flush()
    return row
