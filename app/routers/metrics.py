"""
app/routers/metrics.py
Endpoints de Métricas — alinhado com openapi_v1.yaml.
Implementação stub para Sprint 1; lógica real no Sprint 6.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import MetricsOverviewResponse

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/overview", response_model=MetricsOverviewResponse)
def metrics_overview(db: Session = Depends(get_db)) -> MetricsOverviewResponse:
    # Stub — Sprint 6: calcular KPIs reais via queries agregadas
    return MetricsOverviewResponse()


@router.get("/conversations")
def metrics_conversations(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Stub — Sprint 6
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "detail": "Métricas de conversas serão implementadas no Sprint 6."},
    )


@router.get("/research")
def metrics_research(db: Session = Depends(get_db)) -> JSONResponse:
    # Stub — Sprint 6
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "detail": "Métricas de pesquisa serão implementadas no Sprint 6."},
    )
