"""
app/services/script_loader.py
Carrega a versão ativa de um ResearchScript e fornece acesso aos nós.

Estrutura esperada de definition_json
--------------------------------------
{
  "nodes": {
    "start": {
      "type": "question",           // question | statement | branch | end
      "text": "Qual seu nome?",
      "next": "node_2"              // chave do próximo nó (None se "end")
    },
    "node_2": {
      "type": "question",
      "text": "Qual sua faixa etária?",
      "next": "node_3"
    },
    "node_3": {
      "type": "end",
      "text": "Obrigado pela participação!"
    }
  },
  "start_node": "start"            // nó inicial
}

Alinhamento com extended_models.py
-----------------------------------
    ResearchScript.status            → "draft" | "active" | "archived"
    ResearchScriptVersion.definition_json → JSONB com estrutura acima
    Conversation.current_node_key    → chave do nó corrente
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.extended_models import ResearchScript, ResearchScriptVersion

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScriptNode:
    """Representação de um nó do roteiro."""
    key: str
    node_type: str          # question | statement | branch | end
    text: str               # texto a exibir / enviar
    next_key: str | None    # None se tipo "end" ou sem próximo


@dataclass(frozen=True)
class LoadedScript:
    """Resultado do carregamento — script + versão resolvidos."""
    script_id: str
    version_number: int
    start_node_key: str
    nodes: dict[str, ScriptNode]

    def get_node(self, key: str) -> ScriptNode | None:
        return self.nodes.get(key)

    def start_node(self) -> ScriptNode | None:
        return self.nodes.get(self.start_node_key)


# ---------------------------------------------------------------------------
# Exceções
# ---------------------------------------------------------------------------


class NoActiveScriptError(RuntimeError):
    """Nenhum ResearchScript ativo encontrado para o account_id."""


class InvalidScriptDefinitionError(ValueError):
    """definition_json inválido ou malformado."""


# ---------------------------------------------------------------------------
# ScriptLoader
# ---------------------------------------------------------------------------


class ScriptLoader:
    """
    Carrega o ResearchScript ativo de uma conta e sua versão mais recente.

    Uso
    ---
        loader = ScriptLoader(db)
        loaded = loader.load_active(account_id)
        node   = loaded.get_node(conversation.current_node_key)
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def load_active(self, account_id: Any) -> LoadedScript:
        """
        Busca o ResearchScript com status='active' para account_id
        e retorna a versão com maior version_number.

        Raises
        ------
        NoActiveScriptError
            Se nenhum script ativo existir.
        InvalidScriptDefinitionError
            Se o definition_json estiver malformado.
        """
        # 1. Script ativo
        script_stmt = (
            select(ResearchScript)
            .where(
                ResearchScript.account_id == account_id,
                ResearchScript.status == "active",
            )
            .limit(1)
        )
        script: ResearchScript | None = self._db.scalars(script_stmt).first()
        if script is None:
            raise NoActiveScriptError(
                f"Nenhum ResearchScript ativo para account_id={account_id}."
            )

        # 2. Versão mais recente
        version_stmt = (
            select(ResearchScriptVersion)
            .where(ResearchScriptVersion.script_id == script.id)
            .order_by(ResearchScriptVersion.version_number.desc())
            .limit(1)
        )
        version: ResearchScriptVersion | None = self._db.scalars(version_stmt).first()
        if version is None:
            raise NoActiveScriptError(
                f"ResearchScript id={script.id} não possui versões."
            )

        logger.info(
            "[ScriptLoader] Script carregado: id=%s version=%d",
            script.id,
            version.version_number,
        )
        return self._parse_definition(
            script_id=str(script.id),
            version_number=version.version_number,
            definition=version.definition_json,
        )

    # ------------------------------------------------------------------
    # Parsing interno
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_definition(
        *,
        script_id: str,
        version_number: int,
        definition: dict[str, Any],
    ) -> LoadedScript:
        raw_nodes: dict[str, Any] = definition.get("nodes", {})
        start_node_key: str | None = definition.get("start_node")

        if not raw_nodes:
            raise InvalidScriptDefinitionError(
                "definition_json deve conter 'nodes' não vazio."
            )
        if not start_node_key:
            raise InvalidScriptDefinitionError(
                "definition_json deve conter 'start_node'."
            )

        nodes: dict[str, ScriptNode] = {}
        for key, raw in raw_nodes.items():
            node_type = raw.get("type", "question")
            text = raw.get("text", "")
            next_key = raw.get("next")  # pode ser None para nós "end"
            nodes[key] = ScriptNode(
                key=key,
                node_type=node_type,
                text=text,
                next_key=next_key,
            )

        if start_node_key not in nodes:
            raise InvalidScriptDefinitionError(
                f"'start_node' ({start_node_key!r}) não encontrado em 'nodes'."
            )

        return LoadedScript(
            script_id=script_id,
            version_number=version_number,
            start_node_key=start_node_key,
            nodes=nodes,
        )
