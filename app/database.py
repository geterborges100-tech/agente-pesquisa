"""
app/database.py
Infraestrutura de banco de dados — PostgreSQL 15+ via psycopg2.

DATABASE_URL formato obrigatório:
    postgresql+psycopg2://user:password@host:port/dbname
"""

from __future__ import annotations

import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """Dependência FastAPI: gera sessão e garante fechamento ao fim da request."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables() -> None:
    """Cria tabelas declaradas nos models. Use Alembic em produção."""
    from app.models.models_v1 import Base as AppBase
    from app.models.event import Base as EventBase
    from app.models.extended_models import (
        Handoff, ResearchScript, ResearchScriptVersion, LLMConfig
    )

    AppBase.metadata.create_all(bind=engine)
    EventBase.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas/verificadas com sucesso.")
