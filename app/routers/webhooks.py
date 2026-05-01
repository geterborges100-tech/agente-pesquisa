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
from app.services.evolution_webhook_service import EvolutionAuthError, EvolutionPayloadError, EvolutionWebhookService
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["Webhook"])
EVOLUTION_API_KEY: str = os.environ.get("WEBHOOK_SECRET", os.environ.get("EVOLUTION_API_KEY", ""))
ACCOUNT_ID = uuid.UUID(os.getenv("ACCOUNT_ID", "00000000-0000-0000-0000-000000000001"))


def _build_ai_engine(db: Session) -> AIEngine | None:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        return None
    try:
        llm = LLMClient(
            api_key=key,
            base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            model=os.environ.get("LLM_MODEL", "google/gemini-2.0-flash-001"),
        )
        pb = PromptBuilder(objective="Pesquisa de mercado")
        return AIEngine(llm_client=llm, prompt_builder=pb)
    except Exception as e:
        logger.warning("AIEngine falhou: %s", e)
        return None


def get_evolution_service(db: Session = Depends(get_db)) -> EvolutionWebhookService:
    return EvolutionWebhookService(
        db=db,
        evolution_api_key=EVOLUTION_API_KEY,
        account_id=ACCOUNT_ID,
        conversation_service=ConversationService(),
        ai_engine=_build_ai_engine(db),
    )


@router.post("/evolution/whatsapp", status_code=status.HTTP_200_OK)
async def receive_evolution_webhook(
    request: Request,
    apikey: str | None = Header(None, alias="x-app-secret"),
    evolution_service: EvolutionWebhookService = Depends(get_evolution_service),
) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Payload JSON invalido.") from exc
    try:
        result = await evolution_service.process_event(payload=payload, api_key_header=apikey)
    except EvolutionAuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except EvolutionPayloadError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return JSONResponse(content={"status": "ok", **result})
