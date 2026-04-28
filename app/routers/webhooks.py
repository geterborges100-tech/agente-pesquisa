"""
app/routers/webhooks.py
Rotas de webhook — Meta oficial e Evolution API separados.
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
from app.services.evolution_outbound import EvolutionOutboundClient
from app.services.evolution_webhook_service import (
    EvolutionAuthError,
    EvolutionPayloadError,
    EvolutionWebhookService,
)
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhook"])

EVOLUTION_API_KEY: str = os.environ.get("EVOLUTION_API_KEY", "")
ACCOUNT_ID = uuid.UUID(os.getenv("ACCOUNT_ID", "00000000-0000-0000-0000-000000000001"))


def _build_ai_engine(db: Session) -> AIEngine | None:
    """Instancia o AIEngine com LLMClient e PromptBuilder."""

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_model = os.environ.get("LLM_MODEL", "google/gemini-2.0-flash-001")
    openrouter_base = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not openrouter_key:
        logger.warning("[webhooks_router] OPENROUTER_API_KEY não definida — AIEngine desabilitado.")
        return None

    try:
        llm = LLMClient(
            api_key=openrouter_key,
            base_url=openrouter_base,
            model=openrouter_model,
        )
        prompt_builder = PromptBuilder(objective="Pesquisa de mercado conversacional")
        return AIEngine(llm_client=llm, prompt_builder=prompt_builder)
    except Exception as exc:
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
