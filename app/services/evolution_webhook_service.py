"""
app/services/evolution_webhook_service.py
Processa eventos recebidos da Evolution API v2.3.7.

Diferenças fundamentais em relação ao webhook_service.py (Meta oficial):
- Payload completamente diferente (ver parse abaixo)
- Sem assinatura HMAC confiável — validação via API_KEY header
- remoteJid no formato "556199990000@s.whatsapp.net"

Payload Evolution MESSAGES_UPSERT (referência Sprint 1):
{
  "event": "messages.upsert",
  "instance": "Provedor_CRM",
  "data": {
    "key": {
      "remoteJid": "556199990000@s.whatsapp.net",
      "fromMe": false,
      "id": "WAMID123"
    },
    "message": {"conversation": "Olá, tudo bem?"},
    "pushName": "Nome do Contato",
    "messageTimestamp": 1713312000
  }
}
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
from app.models.models_v1 import Contact
from app.repositories.contact_repository import ContactRepository
from app.services.conversation_service import ConversationService

if TYPE_CHECKING:
    # Import apenas para type-checking — evita import circular em runtime
    from app.services.ai_engine import AIEngine

logger = logging.getLogger(__name__)


# ----
# Exceções
# ----


class EvolutionPayloadError(ValueError):
    """Payload Evolution malformado ou campo obrigatório ausente."""


class EvolutionAuthError(PermissionError):
    """API Key ausente ou inválida."""


# ----
# Modelo normalizado interno
# ----


@dataclass
class NormalizedMessage:
    """Representação interna — independente do provider."""
    external_message_id: str   # key.id  (WAMID)
    sender_phone: str          # remoteJid sem sufixo "@s.whatsapp.net"
    from_me: bool              # key.fromMe
    push_name: str | None      # pushName
    raw_text: str | None       # texto extraído de qualquer tipo suportado
    timestamp: datetime        # messageTimestamp → UTC
    instance: str              # nome da instância Evolution


# ----
# Parser do payload Evolution
# ----


def _clean_jid(remote_jid: str) -> str:
    """Remove sufixo '@s.whatsapp.net' e similares."""
    return remote_jid.split("@")[0]


def _extract_text_from_evolution(data: dict[str, Any]) -> str | None:
    """
    Extrai texto de todos os tipos de mensagem suportados pela Evolution API.

    Tipos mapeados:
    - conversation              → mensagem de texto simples
    - extendedTextMessage.text  → texto com preview de link
    - imageMessage.caption      → legenda de imagem
    - videoMessage.caption      → legenda de vídeo
    - documentMessage.caption   → legenda de documento
    - audioMessage              → None (sem texto)
    - stickerMessage            → None
    """
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
    """
    Converte payload Evolution MESSAGES_UPSERT → NormalizedMessage.

    Raises
    ----
    EvolutionPayloadError
        Se campos obrigatórios estiverem ausentes.
    """
    event = payload.get("event", "")
    if event != "messages.upsert":
        raise EvolutionPayloadError(
            f"Evento não suportado: {event!r}. Esperado: 'messages.upsert'."
        )

    instance = payload.get("instance")
    if not instance:
        raise EvolutionPayloadError("Campo 'instance' ausente no payload.")

    data = payload.get("data", {})
    key = data.get("key", {})

    remote_jid: str | None = key.get("remoteJid")
    if not remote_jid:
        raise EvolutionPayloadError("Campo 'data.key.remoteJid' ausente.")

    message_id: str | None = key.get("id")
    if not message_id:
        raise EvolutionPayloadError("Campo 'data.key.id' ausente.")

    from_me: bool = bool(key.get("fromMe", False))
    push_name: str | None = data.get("pushName")

    raw_text = _extract_text_from_evolution(data)

    ts = data.get("messageTimestamp")
    if ts:
        timestamp = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    else:
        timestamp = datetime.now(tz=timezone.utc)

    return NormalizedMessage(
        external_message_id=message_id,
        sender_phone=_clean_jid(remote_jid),
        from_me=from_me,
        push_name=push_name,
        raw_text=raw_text,
        timestamp=timestamp,
        instance=instance,
    )


# ----
# Validação de API Key (Evolution não usa HMAC)
# ----


def validate_evolution_api_key(
    *,
    received_key: str | None,
    expected_key: str,
) -> None:
    """
    Valida o header 'apikey' enviado pela Evolution API.

    A Evolution API v2 envia o header `apikey` com o valor configurado
    em EVOLUTION_API_KEY no .env. Não há assinatura HMAC.

    Raises
    ----
    EvolutionAuthError
        Se a chave estiver ausente ou não coincidir.
    """
    if not received_key:
        raise EvolutionAuthError("Header 'apikey' ausente.")
    if received_key != expected_key:
        raise EvolutionAuthError("Header 'apikey' inválido.")


# ----
# EvolutionWebhookService
# ----


class EvolutionWebhookService:
    """
    Processa eventos MESSAGES_UPSERT recebidos da Evolution API v2.3.7.

    Pipeline:
    1. Valida API Key.
    2. Parse do payload → NormalizedMessage.
    3. Filtra mensagens enviadas pela própria instância (fromMe=True).
    4. Idempotência via external_event_id na tabela webhook_events.
    5. Upsert do Contact.
    6. ConversationService persiste a mensagem e retorna a Conversation.
    7. AIEngine processa a resposta (se injetado e mensagem tiver texto).
    """

    def __init__(
        self,
        *,
        db: Session,
        evolution_api_key: str,
        account_id: uuid.UUID,
        conversation_service: ConversationService | None = None,
        ai_engine: "AIEngine | None" = None,
    ) -> None:
        self._db = db
        self._evolution_api_key = evolution_api_key
        self._account_id = account_id
        self._conversation_svc = conversation_service or ConversationService()
        self._contact_repo = ContactRepository(db)
        # AIEngine é opcional — permite rodar o webhook sem o motor de IA
        self._ai_engine = ai_engine

    # ----
    # Entrypoint público
    # ----

    def process_event(
        self,
        *,
        payload: dict[str, Any],
        api_key_header: str | None,
    ) -> dict[str, Any]:
        """
        Processa um evento da Evolution API.

        Returns
        ----
        dict com resultado: status, message_id, skipped (bool).
        """
        # 1. Autenticação
        validate_evolution_api_key(
            received_key=api_key_header,
            expected_key=self._evolution_api_key,
        )

        # 2. Parse
        msg = parse_evolution_payload(payload)

        # 3. Filtrar próprias mensagens
        if msg.from_me:
            logger.debug(
                "[Evolution] Mensagem própria ignorada: id=%s", msg.external_message_id
            )
            return {"status": "skipped", "reason": "fromMe=true", "message_id": msg.external_message_id}

        # 4. Idempotência
        event = self._create_event_record(msg)
        if event is None:
            return {"status": "skipped", "reason": "duplicate", "message_id": msg.external_message_id}

        try:
            # 5. Upsert Contact
            contact_id = self._upsert_contact(msg)
            event.contact_id = contact_id

            # 6. ConversationService — persiste mensagem e retorna a Conversation
            conversation = self._conversation_svc.handle_inbound_message(
                db=self._db,
                message=self._to_internal_message(msg),
                contact_id=contact_id,
                event_id=event.id,
            )

            event.status = EventStatus.PROCESSED
            event.processed_at = datetime.now(tz=timezone.utc)
            self._db.commit()

            logger.info(
                "[Evolution] Processado: id=%s phone=%s contact_id=%s",
                msg.external_message_id,
                msg.sender_phone,
                contact_id,
            )

            # 7. AIEngine — chamado APÓS commit (mensagem já durável no banco)
            # Falhas aqui NÃO revertem o registro da mensagem inbound.
            if self._ai_engine is not None and msg.raw_text:
                try:
                    contact = self._db.get(Contact, contact_id)
                    self._ai_engine.process_inbound(
                        conversation=conversation,
                        contact_phone=msg.sender_phone,
                        inbound_text=msg.raw_text,
                        account_id=contact.account_id,
                    )
                except Exception as ai_exc:  # noqa: BLE001
                    logger.exception(
                        "[Evolution] AIEngine falhou para id=%s: %s",
                        msg.external_message_id,
                        ai_exc,
                    )
                    # Intencional: não propaga — evita reentregas desnecessárias

            return {"status": "processed", "message_id": msg.external_message_id}

        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "[Evolution] Falha ao processar id=%s: %s", msg.external_message_id, exc
            )
            event.status = EventStatus.FAILED
            event.error_message = str(exc)
            self._db.commit()
            return {"status": "failed", "message_id": msg.external_message_id, "error": str(exc)}

    # ----
    # Idempotência
    # ----

    def _create_event_record(self, msg: NormalizedMessage) -> WebhookEvent | None:
        event = WebhookEvent(
            external_event_id=msg.external_message_id,
            event_type="messages.upsert",
            status=EventStatus.RECEIVED,
            sender_phone=msg.sender_phone,
            payload_raw=None,
            received_at=datetime.now(tz=timezone.utc),
        )
        try:
            self._db.add(event)
            self._db.flush()
            return event
        except IntegrityError:
            self._db.rollback()
            logger.info(
                "[Evolution] Duplicata ignorada: external_event_id=%s",
                msg.external_message_id,
            )
            return None

    # ----
    # Upsert Contact
    # ----

    def _upsert_contact(self, msg: NormalizedMessage) -> uuid.UUID:
        contact = self._contact_repo.get_by_external_user_id(
            msg.sender_phone, self._account_id
        )
        if contact is None:
            contact = self._contact_repo.create(
                account_id=self._account_id,
                external_user_id=msg.sender_phone,
                full_name=msg.push_name,
                consent_status="pending",
            )
            logger.info(
                "[Evolution] Novo contact: id=%s phone=%s", contact.id, msg.sender_phone
            )
        elif msg.push_name and contact.full_name != msg.push_name:
            self._contact_repo.update(contact.id, {"full_name": msg.push_name})
        return contact.id

    # ----
    # Converter NormalizedMessage → dict interno (ConversationService)
    # ----

    @staticmethod
    def _to_internal_message(msg: NormalizedMessage) -> dict[str, Any]:
        """
        Adapta NormalizedMessage para o formato dict esperado pelo
        ConversationService.handle_inbound_message.
        """
        return {
            "id": msg.external_message_id,
            "from": msg.sender_phone,
            "type": "text",
            "text": {"body": msg.raw_text or ""},
        }
