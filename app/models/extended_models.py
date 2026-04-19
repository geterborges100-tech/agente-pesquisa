"""
app/models/extended_models.py
Modelos adicionais — PostgreSQL 15+ exclusivo.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.models_v1 import Base


class Message(Base):
    """
    Representa uma mensagem individual dentro de uma Conversation.

    direction   : "inbound"  (contact → sistema) | "outbound" (sistema → contact)
    sender_type : "contact" | "ai" | "human_agent" | "system"
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_message_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, unique=True
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class Handoff(Base):
    """Encaminhamento de conversa para agente humano."""

    __tablename__ = "handoffs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="open")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ResearchScript(Base):
    """Roteiro de pesquisa. status: draft → active → archived."""

    __tablename__ = "research_scripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class ResearchScriptVersion(Base):
    """Versão imutável (append-only) de um ResearchScript."""

    __tablename__ = "research_script_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_scripts.id", ondelete="CASCADE"),
        index=True,
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    definition_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        UniqueConstraint("script_id", "version_number", name="uq_script_version"),
    )


class LLMConfig(Base):
    """
    Configuração do provedor LLM por conta.

    Permite trocar modelo/provider/chave sem alterar código — basta
    atualizar o registro no banco e reiniciar o container.

    Campos
    ------
    account_id   : UUID da conta
    provider     : identificador do provedor, ex: "openrouter", "anthropic", "openai"
    base_url     : URL base da API (OpenAI-compatible), ex: "https://openrouter.ai/api/v1"
    model        : identificador do modelo, ex: "google/gemini-2.0-flash-001"
    api_key      : chave de API (armazenada em texto — proteger acesso ao banco)
    max_tokens   : limite de tokens na resposta (padrão: 512)
    is_active    : apenas um registro ativo por account_id deve existir
    notes        : campo livre para documentar a configuração (provider, motivo, etc.)

    Para trocar de modelo/provider
    --------------------------------
    UPDATE llm_configs SET is_active = false WHERE account_id = '<id>' AND is_active = true;
    INSERT INTO llm_configs (account_id, provider, base_url, model, api_key, notes)
    VALUES ('<id>', 'openrouter', 'https://openrouter.ai/api/v1', 'novo/modelo', 'sk-...', 'motivo');
    -- Depois reiniciar o container para recarregar a config.
    """

    __tablename__ = "llm_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    max_tokens: Mapped[int] = mapped_column(nullable=False, server_default="512")
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )