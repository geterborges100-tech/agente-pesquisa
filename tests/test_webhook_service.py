"""
tests/test_webhook_service.py
Testes unitários do WebhookService.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from unittest.mock import MagicMock

import pytest

from app.services.webhook_service import (
    WebhookPayloadError,
    WebhookService,
    WebhookSignatureError,
    validate_signature,
)

SECRET = "test_secret"
ACCOUNT_ID = uuid.uuid4()


def _sign(body: bytes, secret: str = SECRET) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _make_payload(msg_id: str = "wamid.abc123", phone: str = "5511999990000") -> bytes:
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": msg_id,
                                    "from": phone,
                                    "type": "text",
                                    "text": {"body": "Olá"},
                                }
                            ],
                            "contacts": [
                                {
                                    "wa_id": phone,
                                    "profile": {"name": "Teste"},
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }
    return json.dumps(payload).encode()


# ---------------------------------------------------------------------------
# validate_signature
# ---------------------------------------------------------------------------


class TestValidateSignature:
    def test_valid(self):
        body = b"hello"
        validate_signature(
            raw_body=body,
            signature_header=_sign(body),
            app_secret=SECRET,
        )

    def test_missing_header(self):
        with pytest.raises(WebhookSignatureError, match="ausente"):
            validate_signature(raw_body=b"x", signature_header=None, app_secret=SECRET)

    def test_bad_prefix(self):
        with pytest.raises(WebhookSignatureError, match="Formato"):
            validate_signature(raw_body=b"x", signature_header="md5=abc", app_secret=SECRET)

    def test_wrong_digest(self):
        with pytest.raises(WebhookSignatureError, match="inválida"):
            validate_signature(
                raw_body=b"x",
                signature_header="sha256=0000",
                app_secret=SECRET,
            )


# ---------------------------------------------------------------------------
# WebhookService.process_webhook
# ---------------------------------------------------------------------------


class TestWebhookService:
    def _make_service(self, db=None):
        db = db or MagicMock()
        svc = WebhookService(
            db=db,
            app_secret=SECRET,
            account_id=ACCOUNT_ID,  # ← obrigatório (Contact.account_id)
        )
        return svc, db

    def test_invalid_signature_raises(self):
        svc, _ = self._make_service()
        with pytest.raises(WebhookSignatureError):
            svc.process_webhook(raw_body=b"{}", signature_header="sha256=bad")

    def test_invalid_json_raises(self):
        svc, _ = self._make_service()
        body = b"not-json"
        with pytest.raises(WebhookPayloadError):
            svc.process_webhook(raw_body=body, signature_header=_sign(body))

    def test_processes_new_message(self):
        db = MagicMock()
        db.flush = MagicMock()  # não lança IntegrityError → evento novo
        svc, _ = self._make_service(db)

        body = _make_payload()
        result = svc.process_webhook(raw_body=body, signature_header=_sign(body))

        assert result["processed"] == 1
        assert result["skipped"] == 0

    def test_skips_duplicate_message(self):
        from sqlalchemy.exc import IntegrityError

        db = MagicMock()
        db.flush.side_effect = IntegrityError("dup", {}, None)
        svc, _ = self._make_service(db)

        body = _make_payload()
        result = svc.process_webhook(raw_body=body, signature_header=_sign(body))

        assert result["skipped"] == 1
        assert result["processed"] == 0

    def test_message_without_id_is_ignored(self):
        """Mensagem sem campo 'id' não deve gerar evento nem contar como falha."""
        db = MagicMock()
        svc, _ = self._make_service(db)

        payload = {
            "object": "whatsapp_business_account",
            "entry": [{"changes": [{"value": {"messages": [{"from": "5511999990000", "type": "text"}]}}]}],
        }
        body = json.dumps(payload).encode()
        result = svc.process_webhook(raw_body=body, signature_header=_sign(body))

        assert result == {"processed": 0, "skipped": 0, "failed": 0}

    def test_upsert_contact_raises_without_from(self):
        """Mensagem sem 'from' deve resultar em falha (WebhookPayloadError capturado)."""
        db = MagicMock()
        svc, _ = self._make_service(db)

        payload = {
            "object": "whatsapp_business_account",
            "entry": [{"changes": [{"value": {"messages": [{"id": "wamid.xyz", "type": "text"}]}}]}],
        }
        body = json.dumps(payload).encode()
        result = svc.process_webhook(raw_body=body, signature_header=_sign(body))

        assert result["failed"] == 1
