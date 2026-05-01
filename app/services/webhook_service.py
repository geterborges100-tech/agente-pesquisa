"""
app/services/webhook_service.py
Orquestra o processamento seguro de eventos recebidos via Webhook da Meta.

Responsabilidades
-----------------
1. Validar a assinatura HMAC-SHA256 (X-Hub-Signature-256).
2. Garantir idempotência via ``external_event_id`` (tabela ``webhook_events``).
3. Criar / atualizar o ``Contact`` automaticamente (upsert via ContactRepository).
4. Encaminhar para o ``ConversationService`` real.

Alinhamento com models_v1.py
-----------------------------
- Contact.id               → uuid.UUID
- Contact.external_user_id → wa_id do remetente (campo de lookup)
- Contact.full_name         → profile.name vindo do payload
- Contact.account_id        → obrigatório; injetado via WebhookService
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.event import EventStatus, WebhookEvent
from app.repositories.contact_repository import ContactRepository
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------


class WebhookSignatureError(ValueError):
    """Assinatura HMAC inválida ou ausente."""


class WebhookPayloadError(ValueError):
    """Payload malformado ou campo obrigatório ausente."""


# ---------------------------------------------------------------------------
# Validação de assinatura
# ---------------------------------------------------------------------------


def _compute_hmac(secret: str, body: bytes) -> str:
    """Retorna o digest HMAC-SHA256 do payload bruto."""
    return hmac.new(
        key=secret.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()


def validate_signature(
    *,
    raw_body: bytes,
    signature_header: str | None,
    app_secret: str,
) -> None:
    """
    Valida o cabeçalho ``X-Hub-Signature-256`` enviado pela Meta.

    Raises
    ------
    WebhookSignatureError
        Se o cabeçalho estiver ausente ou o digest não coincidir.
    """
    if not signature_header:
        raise WebhookSignatureError("Cabeçalho X-Hub-Signature-256 ausente.")

    prefix = "sha256="
    if not signature_header.startswith(prefix):
        raise WebhookSignatureError(f"Formato de assinatura inesperado: {signature_header!r}")

    received_digest = signature_header[len(prefix) :]
    expected_digest = _compute_hmac(app_secret, raw_body)

    if not hmac.compare_digest(received_digest, expected_digest):
        raise WebhookSignatureError("Assinatura X-Hub-Signature-256 inválida.")


# ---------------------------------------------------------------------------
# Parser de payload Meta WhatsApp / Instagram Cloud API
# ---------------------------------------------------------------------------


def _extract_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Navega na estrutura do payload Meta e devolve a lista de mensagens.

    Estrutura esperada (simplificada):
    {
      "object": "whatsapp_business_account",
      "entry": [{
        "changes": [{
          "value": {
            "messages": [...],
            "contacts": [...]
          }
        }]
      }]
    }
    """
    messages: list[dict[str, Any]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages.extend(value.get("messages", []))
    return messages


def _extract_contacts(payload: dict[str, Any]) -> dict[str, dict]:
    """
    Retorna um mapa {wa_id: contact_info} extraído do payload Meta.
    wa_id é o número de telefone / user_id no formato da Meta.
    """
    contacts: dict[str, dict] = {}
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for c in value.get("contacts", []):
                wa_id = c.get("wa_id")
                if wa_id:
                    contacts[wa_id] = c
    return contacts


# ---------------------------------------------------------------------------
# WebhookService principal
# ---------------------------------------------------------------------------


class WebhookService:
    """
    Ponto central de processamento de webhooks da Meta.

    Parameters
    ----------
    db:
        Sessão SQLAlchemy (injetada pelo caller / DI do FastAPI).
    app_secret:
        ``WHATSAPP_APP_SECRET`` — usado na validação HMAC.
    account_id:
        UUID da conta dona do número — obrigatório em Contact (models_v1.py).
    conversation_service:
        Instância do ConversationService (injetável para testes).
    """

    def __init__(
        self,
        *,
        db: Session,
        app_secret: str,
        account_id: uuid.UUID,
        conversation_service: ConversationService | None = None,
    ) -> None:
        self._db = db
        self._app_secret = app_secret
        self._account_id = account_id
        self._conversation_svc = conversation_service or ConversationService()
        self._contact_repo = ContactRepository(db)

    # ------------------------------------------------------------------
    # Entrypoint público
    # ------------------------------------------------------------------

    def process_webhook(
        self,
        *,
        raw_body: bytes,
        signature_header: str | None,
    ) -> dict[str, Any]:
        """
        Pipeline completo:
        1. Valida assinatura HMAC.
        2. Faz parse do payload.
        3. Para cada mensagem: idempotência → upsert Contact → ConversationService.

        Returns
        -------
        dict com contadores: ``processed``, ``skipped``, ``failed``.
        """
        # 1. Segurança
        validate_signature(
            raw_body=raw_body,
            signature_header=signature_header,
            app_secret=self._app_secret,
        )

        # 2. Parse
        try:
            payload: dict[str, Any] = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise WebhookPayloadError(f"Payload JSON inválido: {exc}") from exc

        messages = _extract_messages(payload)
        contact_map = _extract_contacts(payload)
        payload_str = raw_body.decode(errors="replace")

        results: dict[str, int] = {"processed": 0, "skipped": 0, "failed": 0}

        for message in messages:
            external_id: str | None = message.get("id")
            if not external_id:
                logger.warning("Mensagem sem 'id' ignorada: %s", message)
                continue

            outcome = self._process_single_message(
                message=message,
                contact_map=contact_map,
                payload_str=payload_str,
                external_id=external_id,
            )
            results[outcome] += 1

        logger.info("Webhook processado: %s", results)
        return results

    # ------------------------------------------------------------------
    # Processamento individual
    # ------------------------------------------------------------------

    def _process_single_message(
        self,
        *,
        message: dict[str, Any],
        contact_map: dict[str, dict],
        payload_str: str,
        external_id: str,
    ) -> str:
        """Retorna 'processed' | 'skipped' | 'failed'."""

        # 3. Idempotência
        event = self._create_event_record(
            external_id=external_id,
            message=message,
            payload_str=payload_str,
        )
        if event is None:
            return "skipped"

        try:
            # 4. Upsert Contact → retorna UUID
            wa_id = message.get("from", "")
            contact_id: uuid.UUID = self._upsert_contact(
                wa_id=wa_id,
                contact_info=contact_map.get(wa_id, {}),
            )

            # Persiste o contact_id resolvido no evento
            event.contact_id = contact_id

            # 5. Encaminhar para ConversationService
            self._conversation_svc.handle_inbound_message(
                db=self._db,
                message=message,
                contact_id=contact_id,
                event_id=event.id,
            )

            # 6. Marcar como processado
            event.status = EventStatus.PROCESSED
            event.processed_at = datetime.now(tz=timezone.utc)
            self._db.commit()
            return "processed"

        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha ao processar evento external_id=%s: %s", external_id, exc)
            event.status = EventStatus.FAILED
            event.error_message = str(exc)
            self._db.commit()
            return "failed"

    # ------------------------------------------------------------------
    # Idempotência
    # ------------------------------------------------------------------

    def _create_event_record(
        self,
        *,
        external_id: str,
        message: dict[str, Any],
        payload_str: str,
    ) -> WebhookEvent | None:
        """
        Tenta inserir um ``WebhookEvent``.
        Retorna ``None`` se já existir (duplicata via IntegrityError).
        """
        event = WebhookEvent(
            external_event_id=external_id,
            event_type=message.get("type", "unknown"),
            status=EventStatus.RECEIVED,
            sender_phone=message.get("from"),
            payload_raw=payload_str,
            received_at=datetime.now(tz=timezone.utc),
        )
        try:
            self._db.add(event)
            self._db.flush()  # gera o ID sem commit final
            return event
        except IntegrityError:
            self._db.rollback()
            logger.info("Evento duplicado ignorado: external_event_id=%s", external_id)
            return None

    # ------------------------------------------------------------------
    # Upsert de Contact — via ContactRepository real
    # ------------------------------------------------------------------

    def _upsert_contact(
        self,
        *,
        wa_id: str,
        contact_info: dict[str, Any],
    ) -> uuid.UUID:
        """
        Cria ou atualiza o Contact pelo ``external_user_id`` (wa_id).

        Campos mapeados do payload Meta → Contact (models_v1.py):
        ┌─────────────────────────┬──────────────────────────┐
        │ Payload Meta            │ Contact field            │
        ├─────────────────────────┼──────────────────────────┤
        │ wa_id  (message.from)   │ external_user_id         │
        │ profile.name            │ full_name                │
        │ (injetado via service)  │ account_id               │
        └─────────────────────────┴──────────────────────────┘

        Returns
        -------
        uuid.UUID — contact.id
        """
        if not wa_id:
            raise WebhookPayloadError("Mensagem sem campo 'from' (wa_id).")

        profile = contact_info.get("profile", {})
        full_name = profile.get("name")

        contact = self._contact_repo.get_by_external_user_id(wa_id, self._account_id)

        if contact is None:
            contact = self._contact_repo.create(
                account_id=self._account_id,
                external_user_id=wa_id,
                full_name=full_name,
                consent_status="pending",
            )
            logger.info(
                "[_upsert_contact] Novo contact criado: id=%s wa_id=%s account_id=%s",
                contact.id,
                wa_id,
                self._account_id,
            )
        elif full_name and contact.full_name != full_name:
            self._contact_repo.update(contact.id, {"full_name": full_name})
            logger.info(
                "[_upsert_contact] Contact atualizado: id=%s full_name=%r",
                contact.id,
                full_name,
            )

        return contact.id
