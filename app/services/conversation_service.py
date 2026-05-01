from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.extended_models import Message
from app.models.models_v1 import Contact, Conversation

logger = logging.getLogger(__name__)


class ConversationService:
    def handle_inbound_message(
        self,
        *,
        db: Session,
        message: dict[str, Any],
        contact_id: uuid.UUID,
        event_id: int,
    ) -> Conversation:
        contact = db.get(Contact, contact_id)
        if contact is None:
            raise ValueError(f"Contact não encontrado para contact_id={contact_id}")

        conversation = self._get_or_create_open_conversation(
            db=db,
            contact_id=contact_id,
            account_id=contact.account_id,
        )

        raw_text = self._extract_text(message)

        self._persist_message(
            db=db,
            conversation_id=conversation.id,
            message=message,
            raw_text=raw_text,
        )

        conversation.last_message_at = datetime.now(tz=timezone.utc)
        db.flush()

        logger.info(
            "[ConversationService] event_id=%s contact_id=%s conversation_id=%s",
            event_id,
            contact_id,
            conversation.id,
        )

        return conversation

    def _get_or_create_open_conversation(
        self,
        *,
        db: Session,
        contact_id: uuid.UUID,
        account_id: uuid.UUID,
    ) -> Conversation:
        """
        Retorna a última conversa do contato.
        Se não existir ou estiver fechada, cria uma nova.
        """
        from sqlalchemy import select

        stmt = (
            select(Conversation)
            .where(Conversation.contact_id == contact_id)
            .order_by(Conversation.started_at.desc())
            .limit(1)
        )
        conversation = db.scalars(stmt).first()

        if conversation is None or conversation.status == "closed":
            conversation = Conversation(
                account_id=account_id,
                contact_id=contact_id,
                status="open",
                channel="instagram",
            )
            db.add(conversation)
            db.flush()
            logger.info(
                "[ConversationService] Nova conversa criada: id=%s contact_id=%s",
                conversation.id,
                contact_id,
            )
        else:
            logger.info(
                "[ConversationService] Reutilizando conversa existente: id=%s status=%s",
                conversation.id,
                conversation.status,
            )

        return conversation

    @staticmethod
    def _extract_text(message: dict[str, Any]) -> str | None:
        msg_type = message.get("type", "")
        if msg_type == "text":
            return message.get("text", {}).get("body")
        if msg_type in {"image", "video", "document"}:
            return message.get(msg_type, {}).get("caption")
        return None

    @staticmethod
    def _persist_message(
        *,
        db: Session,
        conversation_id: uuid.UUID,
        message: dict[str, Any],
        raw_text: str | None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            direction="inbound",
            sender_type="contact",
            raw_text=raw_text,
            external_message_id=message.get("id"),
        )
        db.add(msg)
        db.flush()
        return msg
