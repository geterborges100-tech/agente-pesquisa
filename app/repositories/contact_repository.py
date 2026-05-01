"""
app/repositories/contact_repository.py
CRUD para a entidade Contact, alinhado com models_v1.py.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models_v1 import Contact


class ContactRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def get_by_id(self, contact_id: uuid.UUID) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        return self._db.scalars(stmt).first()

    def get_by_external_user_id(
        self,
        wa_id: str,
        account_id: uuid.UUID,
    ) -> Contact | None:
        """
        Busca por external_user_id AND account_id — nunca só um dos dois.
        Evita colisão entre contas distintas que recebam o mesmo wa_id.
        """
        stmt = select(Contact).where(
            Contact.external_user_id == wa_id,
            Contact.account_id == account_id,
        )
        return self._db.scalars(stmt).first()

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        account_id: uuid.UUID,
        external_user_id: str,
        full_name: str | None = None,
        consent_status: str = "pending",
    ) -> Contact:
        contact = Contact(
            account_id=account_id,
            external_user_id=external_user_id,
            full_name=full_name,
            consent_status=consent_status,
        )
        self._db.add(contact)
        self._db.flush()  # popula contact.id sem commit final
        return contact

    def update(self, contact_id: uuid.UUID, data: dict[str, Any]) -> Contact:
        """
        Atualiza campos arbitrários do Contact.
        Raises ValueError se o contato não for encontrado.
        """
        contact = self.get_by_id(contact_id)
        if contact is None:
            raise ValueError(f"Contact não encontrado: {contact_id}")

        allowed = {
            "full_name",
            "username",
            "consent_status",
            "segment",
            "lead_score",
        }
        for key, value in data.items():
            if key not in allowed:
                raise ValueError(f"Campo não permitido para update: {key!r}")
            setattr(contact, key, value)

        self._db.flush()
        return contact
