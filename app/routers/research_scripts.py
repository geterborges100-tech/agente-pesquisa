"""
app/routers/research_scripts.py
Endpoints de Research Scripts — alinhado com openapi_v1.yaml.
"""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.extended_models import ResearchScript, ResearchScriptVersion
from app.schemas.schemas import (
    ResearchScriptCreate,
    ResearchScriptResponse,
    ResearchScriptVersionCreate,
    ResearchScriptVersionResponse,
)

router = APIRouter(prefix="/research-scripts", tags=["ResearchScripts"])

# account_id padrão injetado via env (mesmo padrão do main.py)
_ACCOUNT_ID = uuid.UUID(os.getenv("ACCOUNT_ID", "00000000-0000-0000-0000-000000000001"))


@router.get("", response_model=list[ResearchScriptResponse])
def list_scripts(db: Session = Depends(get_db)) -> list[ResearchScriptResponse]:
    scripts = db.scalars(select(ResearchScript)).all()
    return [ResearchScriptResponse.model_validate(s) for s in scripts]


@router.post("", response_model=ResearchScriptResponse, status_code=status.HTTP_201_CREATED)
def create_script(
    body: ResearchScriptCreate,
    db: Session = Depends(get_db),
) -> ResearchScriptResponse:
    script = ResearchScript(
        account_id=_ACCOUNT_ID,
        name=body.name,
        description=body.description,
        objective=body.objective,
        status="draft",
    )
    db.add(script)
    db.commit()
    db.refresh(script)
    return ResearchScriptResponse.model_validate(script)


@router.post(
    "/{script_id}/versions",
    response_model=ResearchScriptVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_script_version(
    script_id: uuid.UUID,
    body: ResearchScriptVersionCreate,
    db: Session = Depends(get_db),
) -> ResearchScriptVersionResponse:
    script = db.get(ResearchScript, script_id)
    if script is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roteiro não encontrado.")

    # Calcula próximo version_number
    stmt = (
        select(ResearchScriptVersion.version_number)
        .where(ResearchScriptVersion.script_id == script_id)
        .order_by(ResearchScriptVersion.version_number.desc())
        .limit(1)
    )
    last_version = db.scalar(stmt)
    next_version = (last_version or 0) + 1

    version = ResearchScriptVersion(
        script_id=script_id,
        version_number=next_version,
        definition_json=body.definition_json,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return ResearchScriptVersionResponse.model_validate(version)
