"""
app/services/evolution_webhook_service.py
Processa eventos recebidos da Evolution API v2.3.7.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.event import EventStatus, WebhookEvent
from app.models.models_v1 import Contact, Conversation
from app.repositories.consent_repository import ConsentRepository
from app.repositories.contact_repository import ContactRepository
from app.services.conversation_service import ConversationService
from app.services.evolution_outbound import EvolutionOutboundClient
from app.services.guardrail_validator import GuardrailValidator

if TYPE_CHECKING:
    from app.services.ai_engine import AIEngine

logger = logging.getLogger(__name__)

LGPD_MESSAGE = (
    "Ola! Antes de continuar, preciso do seu consentimento para processar seus dados "
    "conforme a LGPD. Voce concorda? Responda *sim* para aceitar ou *nao* para recusar."
)
CONSENT_DENIED_MESSAGE = "Entendido. Seus dados nao serao processados. Ate logo!"
CONSENT_GRANTED_MESSAGE = "Obrigado! Consentimento registrado. Como posso ajudar?"


class EvolutionPayloadError(ValueError):
    """Payload Evolution malformado."""


class EvolutionAuthError(PermissionError):
    """API Key ausente ou invalida."""


@dataclass
class NormalizedMessage:
    external_message_id: str
    sender_phone: str
    from_me: bool
    push_name: str | None
    raw_text: str | None
    timestamp: datetime
    instance: str


def _clean_jid(remote_jid: str) -> str:
    return remote_jid.split("@")[0]


def _extract_text_from_evolution(data: dict[str, Any]) -> str | None:
    msg = data.get("message", {})
    if not msg:
        return None
    if "conversation" in msg:
        return msg["conversation"]
    if "extendedTextMessage" in msg:
        return msg["extendedTextMessage"].get("text")
    for media in ("imageMessage", "videoMessage", "documentMessage"):
        if media in msg:
            return msg[media].get("caption")
    return None


def parse_evolution_payload(payload: dict[str, Any]) -> NormalizedMessage:
    event = payload.get("event", "")
    if event != "messages.upsert":
        raise EvolutionPayloadError(f"Evento nao suportado: {event!r}.")

    instance = payload.get("instance")
    if not instance:
        raise EvolutionPayloadError("Campo 'instance' ausente no payload.")

    data = payload.get("data", {})
    key = data.get("key", {})

    remote_jid = key.get("remoteJid")
    if not remote_jid:
        raise EvolutionPayloadError("Campo 'data.key.remoteJid' ausente.")

    message_id = key.get("id")
    if not message_id:
        raise EvolutionPayloadError("Campo 'data.key.id' ausente.")

    from_me = bool(key.get("fromMe", False))
    push_name = data.get("pushName")
    raw_text = _extract_text_from_evolution(data)

    ts = data.get("messageTimestamp")
    timestamp = datetime.fromtimestamp(int(ts), tz=timezone.utc) if ts else datetime.now(tz=timezone.utc)

    return NormalizedMessage(
        external_message_id=message_id,
        sender_phone=_clean_jid(remote_jid),
        from_me=from_me,
        push_name=push_name,
        raw_text=raw_text,
        timestamp=timestamp,
        instance=instance,
    )


def validate_evolution_api_key(*, received_key: str | None, expected_key: str) -> None:
    if not received_key:
        raise EvolutionAuthError("Header 'apikey' ausente.")
    if received_key != expected_key:
        raise EvolutionAuthError("Header 'apikey' invalido.")


class EvolutionWebhookService:
    """Processa eventos MESSAGES_UPSERT recebidos da Evolution API v2.3.7."""

    def __init__(
        self,
        *,
        db: Session,
        evolution_api_key: str,
        account_id: uuid.UUID,
        conversation_service: ConversationService | None = None,
        ai_engine: AIEngine | None = None,
    ) -> None:
        self._db = db
        self._evolution_api_key = evolution_api_key
        self._account_id = account_id
        self._conversation_svc = conversation_service or ConversationService()
        self._contact_repo = ContactRepository(db)
        self._consent_repo = ConsentRepository(db)
        self._guardrail = GuardrailValidator()
        self._ai_engine = ai_engine
        self._outbound = EvolutionOutboundClient()

    def _send(self, number: str, text: str) -> None:
        try:
            self._outbound.send_text(number=number, text=text)
        except Exception as exc:
            logger.error("[Evolution] Falha ao enviar mensagem outbound: %s", exc)

    async def process_event(self, *, payload: dict[str, Any], api_key_header: str | None) -> dict[str, Any]:
        validate_evolution_api_key(received_key=api_key_header, expected_key=self._evolution_api_key)
        msg = parse_evolution_payload(payload)

        if msg.from_me:
            return {"status": "skipped", "reason": "fromMe=true", "message_id": msg.external_message_id}

        event = self._create_event_record(msg)
        if event is None:
            return {"status": "skipped", "reason": "duplicate", "message_id": msg.external_message_id}

        try:
            contact_id = self._upsert_contact(msg)
            event.contact_id = contact_id

            conversation = self._conversation_svc.handle_inbound_message(
                db=self._db,
                message=self._to_internal_message(msg),
                contact_id=contact_id,
                event_id=event.id,
            )

            event.status = EventStatus.PROCESSED
            event.processed_at = datetime.now(tz=timezone.utc)
            self._db.commit()

            if msg.raw_text:
                contact = self._db.get(Contact, contact_id)
                consent_result = self._handle_consent_logic(contact, msg.raw_text, conversation.id)

                if consent_result is not None:
                    status = consent_result.get("status")
                    if status == "awaiting_consent":
                        self._send(msg.sender_phone, LGPD_MESSAGE)
                    elif status == "consent_denied":
                        self._send(msg.sender_phone, CONSENT_DENIED_MESSAGE)
                    elif status == "consent_granted":
                        self._send(msg.sender_phone, CONSENT_GRANTED_MESSAGE)
                    return {**consent_result, "message_id": msg.external_message_id}

                if self._ai_engine is not None:
                    try:
                        result = await self._ai_engine.process_inbound(
                            db=self._db,
                            conversation=conversation,
                            message_text=msg.raw_text,
                            script={},
                        )
                        outbound_text = result.get("outbound_text")
                        if outbound_text:
                            self._send(msg.sender_phone, outbound_text)
                    except Exception as ai_exc:
                        logger.exception("[Evolution] AIEngine falhou: %s", ai_exc)
                else:
                    logger.warning("[Evolution] AIEngine nao configurado - OPENROUTER_API_KEY ausente?")

            return {"status": "processed", "message_id": msg.external_message_id}

        except Exception as exc:
            logger.exception("[Evolution] Falha: %s", exc)
            event.status = EventStatus.FAILED
            event.error_message = str(exc)
            self._db.commit()
            return {"status": "failed", "message_id": msg.external_message_id, "error": str(exc)}

    def _create_event_record(self, msg: NormalizedMessage) -> WebhookEvent | None:
        event = WebhookEvent(
            external_event_id=msg.external_message_id,
            event_type="messages.upsert",
            status=EventStatus.RECEIVED,
            sender_phone=msg.sender_phone,
            received_at=datetime.now(tz=timezone.utc),
        )
        try:
            self._db.add(event)
            self._db.flush()
            return event
        except IntegrityError:
            self._db.rollback()
            return None

    def _upsert_contact(self, msg: NormalizedMessage) -> uuid.UUID:
        contact = self._contact_repo.get_by_external_user_id(msg.sender_phone, self._account_id)
        if contact is None:
            contact = self._contact_repo.create(
                account_id=self._account_id,
                external_user_id=msg.sender_phone,
                full_name=msg.push_name,
                consent_status="pending",
            )
        elif msg.push_name and contact.full_name != msg.push_name:
            self._contact_repo.update(contact.id, {"full_name": msg.push_name})
        return contact.id

    @staticmethod
    def _to_internal_message(msg: NormalizedMessage) -> dict[str, Any]:
        return {
            "id": msg.external_message_id,
            "from": msg.sender_phone,
            "type": "text",
            "text": {"body": msg.raw_text or ""},
        }

    def _handle_consent_logic(self, contact, text_content: str, conversation_id: uuid.UUID) -> dict | None:
        if self._consent_repo.has_granted(contact_id=contact.id, type="lgpd"):
            return None

        clean_text = text_content.strip().lower()

        if clean_text in ["sim", "aceito", "concordo", "s"]:
            self._consent_repo.create_and_commit(
                contact_id=contact.id,
                conversation_id=conversation_id,
                type="lgpd",
                status="granted",
                purpose="atendimento_geral",
            )
            return {"status": "consent_granted"}

        if clean_text in ["nao", "nao", "recuso", "n"]:
            self._consent_repo.create_and_commit(
                contact_id=contact.id,
                conversation_id=conversation_id,
                type="lgpd",
                status="denied",
            )
            conv = self._db.get(Conversation, conversation_id)
            if conv:
                conv.status = "closed"
                self._db.flush()
            return {"status": "consent_denied", "reason": "user_refused"}

        return {"status": "awaiting_consent"}
