"""
app/routers/webhooks.py
Rotas de webhook — Meta oficial e Evolution API separados.

GET  /webhooks/meta/instagram        → handshake Meta (mantido em main.py)
POST /webhooks/meta/instagram        → eventos Meta (mantido em main.py)
POST /webhooks/evolution/whatsapp    → eventos Evolution API v2.3.7
"""

from __future__ import annotations

import logging
import os
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_engine import AIEngine
from app.services.conversation_service import ConversationService
from app.services.evolution_outbound import EvolutionOutboundClient, OutboundError
from app.services.evolution_webhook_service import (
    EvolutionAuthError,
    EvolutionPayloadError,
    EvolutionWebhookService,
)
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhook"])

EVOLUTION_API_KEY: str = os.environ.get("EVOLUTION_API_KEY", "")
ACCOUNT_ID = uuid.UUID(os.getenv("ACCOUNT_ID", "00000000-0000-0000-0000-000000000001"))


def _build_ai_engine(db: Session) -> AIEngine | None:
    """
    Instancia o AIEngine se as variáveis de ambiente necessárias estiverem
    configuradas. Retorna None em caso de configuração ausente (fallback
    silencioso — o webhook ainda processa a mensagem, só não responde via IA).
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    evolution_base = os.environ.get("EVOLUTION_BASE_URL", "")
    evolution_instance = os.environ.get("EVOLUTION_INSTANCE", "Provedor_CRM")

    if not anthropic_key:
        logger.warning("[webhooks_router] ANTHROPIC_API_KEY não definida — AIEngine desabilitado.")
        return None

    if not evolution_base:
        logger.warning("[webhooks_router] EVOLUTION_BASE_URL não definida — AIEngine desabilitado.")
        return None

    try:
        llm = LLMClient(api_key=anthropic_key)
        outbound = EvolutionOutboundClient(
            base_url=evolution_base,
            api_key=EVOLUTION_API_KEY,
            instance=evolution_instance,
        )
        return AIEngine(db=db, llm_client=llm, outbound_client=outbound)
    except OutboundError as exc:
        logger.warning("[webhooks_router] Falha ao criar AIEngine: %s", exc)
        return None


def get_evolution_service(db: Session = Depends(get_db)) -> EvolutionWebhookService:
    return EvolutionWebhookService(
        db=db,
        evolution_api_key=EVOLUTION_API_KEY,
        account_id=ACCOUNT_ID,
        conversation_service=ConversationService(),
        ai_engine=_build_ai_engine(db),
    )


@router.post(
    "/evolution/whatsapp",
    summary="Recebe eventos da Evolution API v2.3.7",
    status_code=status.HTTP_200_OK,
)
async def receive_evolution_webhook(
    request: Request,
    apikey: str | None = Header(None, alias="apikey"),
    evolution_service: EvolutionWebhookService = Depends(get_evolution_service),
) -> JSONResponse:
    """
    Recebe eventos MESSAGES_UPSERT da Evolution API.

    Segurança: valida header `apikey` configurado em EVOLUTION_API_KEY.
    A Evolution API envia este header em todas as requisições de webhook.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON inválido.",
        )

    try:
        result = evolution_service.process_event(
            payload=payload,
            api_key_header=apikey,
        )
    except EvolutionAuthError as exc:
        logger.warning("[Evolution] Auth falhou: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except EvolutionPayloadError as exc:
        logger.warning("[Evolution] Payload inválido: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return JSONResponse(content={"status": "ok", **result})
