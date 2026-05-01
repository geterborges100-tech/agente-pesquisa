from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models_v1 import Consent


class ConsentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        contact_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
        type: str,
        status: str,
        purpose: str | None = None,
        legal_basis: str = "consent",
        channel_message_id: str | None = None,
    ) -> Consent:
        consent = Consent(
            contact_id=contact_id,
            conversation_id=conversation_id,
            type=type,
            status=status,
            purpose=purpose,
            legal_basis=legal_basis,
            channel_message_id=channel_message_id,
        )
        self._db.add(consent)
        self._db.flush()
        return consent

    def create_and_commit(
        self,
        *,
        contact_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
        type: str,
        status: str,
        purpose: str | None = None,
        legal_basis: str = "consent",
        channel_message_id: str | None = None,
    ) -> Consent:
        consent = Consent(
            contact_id=contact_id,
            conversation_id=conversation_id,
            type=type,
            status=status,
            purpose=purpose,
            legal_basis=legal_basis,
            channel_message_id=channel_message_id,
        )
        self._db.add(consent)
        self._db.commit()
        return consent

    def get_latest(self, *, contact_id: uuid.UUID, type: str) -> Consent | None:
        stmt = (
            select(Consent)
            .where(Consent.contact_id == contact_id, Consent.type == type)
            .order_by(Consent.created_at.desc())
            .limit(1)
        )
        return self._db.scalars(stmt).first()

    def has_granted(self, *, contact_id: uuid.UUID, type: str) -> bool:
        c = self.get_latest(contact_id=contact_id, type=type)
        return bool(c and c.status == "granted")

    def has_denied(self, *, contact_id: uuid.UUID, type: str) -> bool:
        c = self.get_latest(contact_id=contact_id, type=type)
        return bool(c and c.status == "denied")
