"""
app/schemas/schemas.py
Pydantic v2 schemas — alinhados com openapi_v1.yaml.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_user_id: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    consent_status: str
    segment: Optional[str] = None
    lead_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class ContactUpdate(BaseModel):
    segment: Optional[str] = None
    lead_score: Optional[float] = None
    profile_summary: Optional[str] = None


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contact_id: uuid.UUID
    channel: str
    status: str
    current_node_key: Optional[str] = None
    started_at: datetime
    last_message_at: datetime
    ended_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    sender_type: str
    raw_text: Optional[str] = None
    sent_at: datetime


class SendMessageRequest(BaseModel):
    text: str
    sender_type: str = "human_agent"  # "human_agent" | "system"


# ---------------------------------------------------------------------------
# Handoff
# ---------------------------------------------------------------------------


class HandoffRequest(BaseModel):
    reason: Optional[str] = None
    assigned_to: Optional[str] = None


class HandoffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    reason: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Research Scripts
# ---------------------------------------------------------------------------


class ResearchScriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    objective: str
    status: str
    created_at: datetime
    updated_at: datetime


class ResearchScriptCreate(BaseModel):
    name: str
    description: Optional[str] = None
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
