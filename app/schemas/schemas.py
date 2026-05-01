"""
app/schemas/schemas.py
Pydantic v2 schemas — alinhados com openapi_v1.yaml.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_user_id: str
    username: str | None = None
    full_name: str | None = None
    consent_status: str
    segment: str | None = None
    lead_score: float | None = None
    created_at: datetime
    updated_at: datetime


class ContactUpdate(BaseModel):
    segment: str | None = None
    lead_score: float | None = None
    profile_summary: str | None = None


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contact_id: uuid.UUID
    channel: str
    status: str
    current_node_key: str | None = None
    started_at: datetime
    last_message_at: datetime
    ended_at: datetime | None = None


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    sender_type: str
    raw_text: str | None = None
    sent_at: datetime


class SendMessageRequest(BaseModel):
    text: str
    sender_type: str = "human_agent"  # "human_agent" | "system"


# ---------------------------------------------------------------------------
# Handoff
# ---------------------------------------------------------------------------


class HandoffRequest(BaseModel):
    reason: str | None = None
    assigned_to: str | None = None


class HandoffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    reason: str | None = None
    status: str
    assigned_to: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None


# ---------------------------------------------------------------------------
# Research Scripts
# ---------------------------------------------------------------------------


class ResearchScriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    objective: str
    status: str
    created_at: datetime
    updated_at: datetime


class ResearchScriptCreate(BaseModel):
    name: str
    description: str | None = None
    objective: str


class ResearchScriptVersionCreate(BaseModel):
    definition_json: dict[str, Any]


class ResearchScriptVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    script_id: uuid.UUID
    version_number: int
    definition_json: dict[str, Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class MetricsOverviewResponse(BaseModel):
    total_conversations: int = 0
    open_conversations: int = 0
    completion_rate: float = 0.0
    avg_duration_minutes: float = 0.0
    handoff_rate: float = 0.0
    extraction_accuracy_rate: float = 0.0


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class PaginatedContacts(BaseModel):
    data: list[ContactResponse]
    total: int


class PaginatedConversations(BaseModel):
    data: list[ConversationResponse]
    total: int
