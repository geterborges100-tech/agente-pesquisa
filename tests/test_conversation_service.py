"""
tests/test_conversation_service.py
Testes unitários do ConversationService.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.services.conversation_service import ConversationService, Message
from app.models.models_v1 import Contact, Conversation

ACCOUNT_ID  = uuid.uuid4()
CONTACT_ID  = uuid.uuid4()
CONV_ID     = uuid.uuid4()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_contact(contact_id: uuid.UUID = CONTACT_ID) -> MagicMock:
    c = MagicMock(spec=Contact)
    c.id         = contact_id
    c.account_id = ACCOUNT_ID
    return c


def _make_conversation(
    contact_id: uuid.UUID = CONTACT_ID,
    status: str = "open",
) -> MagicMock:
    conv = MagicMock(spec=Conversation)
    conv.id              = CONV_ID
    conv.contact_id      = contact_id
    conv.account_id      = ACCOUNT_ID
    conv.status          = status
    conv.last_message_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return conv


def _make_message(msg_id: str = "wamid.abc", phone: str = "5511999990000") -> dict:
    return {
        "id":   msg_id,
        "from": phone,
        "type": "text",
        "text": {"body": "Olá"},
    }


def _make_db(contact: MagicMock, conversation: MagicMock | None) -> MagicMock:
    db = MagicMock()
    db.get.return_value = contact

    # scalars().first() → conversa existente ou None
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = conversation
    db.scalars.return_value = scalars_mock

    return db


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestHandleInboundMessage:

    def test_uses_existing_open_conversation(self):
        """Mensagem em conversa existente (open): não cria nova conversa."""
        contact  = _make_contact()
        conv     = _make_conversation()
        db       = _make_db(contact, conv)
        svc      = ConversationService()
        message  = _make_message()

        svc.handle_inbound_message(
            db=db, message=message, contact_id=CONTACT_ID, event_id=1
        )

        # Conversation não foi adicionada ao db (já existia)
        added_types = [type(c[0][0]) for c in db.add.call_args_list]
        assert Conversation not in added_types

        # Message foi persistida
        assert Message in added_types

    def test_creates_new_conversation_when_none_open(self):
        """Sem conversa aberta → cria Conversation nova."""
        contact = _make_contact()
        db      = _make_db(contact, conversation=None)
        svc     = ConversationService()
        message = _make_message()

        svc.handle_inbound_message(
            db=db, message=message, contact_id=CONTACT_ID, event_id=2
        )

        added_types = [type(c[0][0]) for c in db.add.call_args_list]
        assert Conversation in added_types
        assert Message in added_types

    def test_last_message_at_is_updated(self):
        """last_message_at deve ser atualizado após processar a mensagem."""
        contact = _make_contact()
        conv    = _make_conversation()
        db      = _make_db(contact, conv)
        svc     = ConversationService()

        before = conv.last_message_at
        svc.handle_inbound_message(
            db=db, message=_make_message(), contact_id=CONTACT_ID, event_id=3
        )

        assert conv.last_message_at > before

    def test_raises_if_contact_not_found(self):
        """Deve lançar ValueError se o Contact não existir no banco."""
        db = MagicMock()
        db.get.return_value = None
        svc = ConversationService()

        with pytest.raises(ValueError, match="Contact não encontrado"):
            svc.handle_inbound_message(
                db=db,
                message=_make_message(),
                contact_id=uuid.uuid4(),
                event_id=4,
            )

    def test_raw_text_extracted_from_text_message(self):
        """raw_text deve conter o body da mensagem de texto."""
        contact = _make_contact()
        conv    = _make_conversation()
        db      = _make_db(contact, conv)
        svc     = ConversationService()

        svc.handle_inbound_message(
            db=db,
            message={"id": "wamid.x", "from": "551199", "type": "text", "text": {"body": "Oi!"}},
            contact_id=CONTACT_ID,
            event_id=5,
        )

        msg_obj: Message = next(
            c[0][0] for c in db.add.call_args_list if isinstance(c[0][0], Message)
        )
        assert msg_obj.raw_text == "Oi!"

    def test_raw_text_none_for_unknown_type(self):
        """Tipos desconhecidos não devem causar erro; raw_text fica None."""
        contact = _make_contact()
        conv    = _make_conversation()
        db      = _make_db(contact, conv)
        svc     = ConversationService()

        svc.handle_inbound_message(
            db=db,
            message={"id": "wamid.y", "from": "551199", "type": "location"},
            contact_id=CONTACT_ID,
            event_id=6,
        )

        msg_obj: Message = next(
            c[0][0] for c in db.add.call_args_list if isinstance(c[0][0], Message)
        )
        assert msg_obj.raw_text is None

    def test_new_conversation_has_correct_fields(self):
        """Conversa nova deve herdar account_id e status='open'."""
        contact = _make_contact()
        db      = _make_db(contact, conversation=None)
        svc     = ConversationService()

        svc.handle_inbound_message(
            db=db, message=_make_message(), contact_id=CONTACT_ID, event_id=7
        )

        conv_obj: Conversation = next(
            c[0][0] for c in db.add.call_args_list if isinstance(c[0][0], Conversation)
        )
        assert conv_obj.account_id == ACCOUNT_ID
        assert conv_obj.contact_id == CONTACT_ID
        assert conv_obj.status == "open"


# ---------------------------------------------------------------------------
# Testes unitários de _extract_text
# ---------------------------------------------------------------------------


class TestExtractText:
    def test_text_message(self):
        assert ConversationService._extract_text(
            {"type": "text", "text": {"body": "Hello"}}
        ) == "Hello"

    def test_image_with_caption(self):
        assert ConversationService._extract_text(
            {"type": "image", "image": {"caption": "foto"}}
        ) == "foto"

    def test_sticker_returns_none(self):
        assert ConversationService._extract_text({"type": "sticker"}) is None
