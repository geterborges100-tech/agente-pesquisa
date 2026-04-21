from __future__ import annotations
import uuid
from typing import Any
from sqlalchemy.orm import Session
from app.models.models_v1 import AuditLog

def log_event(db: Session, *, event: str, actor: str, entity: str, entity_id: uuid.UUID, action: str, criticality: str = "medium", conversation_id: uuid.UUID | None = None, context: dict[str, Any] | None = None) -> AuditLog:
    row = AuditLog(event=event, actor=actor, entity=entity, entity_id=entity_id, action=action, criticality=criticality, conversation_id=conversation_id, context=context)
    db.add(row)
    db.flush()
    return row
