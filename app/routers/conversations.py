"""
app/routers/conversations.py
Endpoints de Conversations — alinhado com openapi_v1.yaml.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.extended_models import Message
from app.models.models_v1 import Conversation
from app.schemas.schemas import (
    ConversationResponse,
    HandoffRequest,
    MessageResponse,
    PaginatedConversations,
    SendMessageRequest,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=PaginatedConversations)
def list_conversations(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedConversations:
    stmt = select(Conversation)
    if status_filter:
        stmt = stmt.where(Conversation.status == status_filter)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    conversations = db.scalars(stmt.offset((page - 1) * limit).limit(limit)).all()

    return PaginatedConversations(
        data=[ConversationResponse.model_validate(c) for c in conversations],
        total=total or 0,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    conv = db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")
    return ConversationResponse.model_validate(conv)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[MessageResponse]:
    conv = db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")

    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.sent_at.asc())
    messages = db.scalars(stmt).all()
    return [MessageResponse.model_validate(m) for m in messages]


@router.post("/{conversation_id}/messages/send", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def send_message(
    conversation_id: uuid.UUID,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Stub — Sprint 2: integração com Meta API para envio outbound
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"status": "not_implemented", "detail": "Envio outbound será implementado no Sprint 2."},
    )


@router.post("/{conversation_id}/handoff", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_handoff(
    conversation_id: uuid.UUID,
    body: HandoffRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Stub — Sprint 4: detecção e gestão de handoffs
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"status": "not_implemented", "detail": "Handoff será implementado no Sprint 4."},
    )


@router.post("/{conversation_id}/close", status_code=status.HTTP_200_OK)
def close_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict:
    conv = db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")

    if conv.status in ("closed", "abandoned"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conversa já está com status '{conv.status}'.",
        )

    conv.status = "closed"
    from datetime import datetime, timezone

    conv.ended_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(conv)

    return {"status": "ok", "conversation_id": str(conv.id), "new_status": conv.status}
