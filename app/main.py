"""
app/main.py — Sprint 3 wiring
"""

from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.database import create_all_tables, get_db
from app.routers import contacts, conversations, metrics, research_scripts
from app.routers.webhooks import router as webhooks_router
from app.services.conversation_service import ConversationService
from app.services.webhook_service import WebhookPayloadError, WebhookService, WebhookSignatureError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)
APP_SECRET = os.environ["APP_SECRET"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
ACCOUNT_ID = uuid.UUID(os.getenv("ACCOUNT_ID", "00000000-0000-0000-0000-000000000001"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando — criando tabelas se necessário…")
    create_all_tables()
    logger.info("✅ Banco de dados pronto.")
    yield
    logger.info("🛑 Aplicação encerrada.")


app = FastAPI(title="Agente de Pesquisa", version="3.0.0", lifespan=lifespan)
app.include_router(contacts.router)
app.include_router(conversations.router)
app.include_router(research_scripts.router)
app.include_router(metrics.router)
app.include_router(webhooks_router)


def get_webhook_service(db: Session = Depends(get_db)) -> WebhookService:
    return WebhookService(
        db=db, app_secret=APP_SECRET, account_id=ACCOUNT_ID, conversation_service=ConversationService()
    )


@app.get("/webhooks/meta/instagram", tags=["Webhook"], response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge or "", status_code=200)
    raise HTTPException(status_code=403, detail="Token inválido.")


@app.post("/webhooks/meta/instagram", tags=["Webhook"], status_code=200)
async def receive_webhook_meta(
    request: Request,
    x_hub_signature_256: Annotated[str | None, Header()] = None,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    raw_body = await request.body()
    try:
        result = webhook_service.process_webhook(raw_body=raw_body, signature_header=x_hub_signature_256)
    except (WebhookSignatureError, WebhookPayloadError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse(content={"status": "ok", **result})


@app.get("/health", tags=["Infra"])
def health_check():
    return {"status": "healthy"}
