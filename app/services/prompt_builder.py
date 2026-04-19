"""
app/services/prompt_builder.py
Monta o prompt completo para o LLM (Anthropic Claude).

Responsabilidades
-----------------
1. Montar system prompt com objetivo do roteiro e instrução de persona.
2. Construir histórico de mensagens no formato Anthropic Messages API.
3. Injetar o nó atual (pergunta/statement) no último turno do usuário.

Formato de saída (usado por LLMClient)
---------------------------------------
{
  "system": "<system prompt>",
  "messages": [
    {"role": "user",      "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
    {"role": "user",      "content": "<última mensagem + instrução do nó>"}
  ]
}
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.script_loader import LoadedScript, ScriptNode

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATE = """\
Você é um assistente de pesquisa de mercado conversacional. \
Seu objetivo é coletar respostas dos participantes seguindo o roteiro abaixo \
de forma natural e empática, sem revelar que é uma IA a não ser que perguntado.

OBJETIVO DO ROTEIRO:
{objective}

REGRAS:
- Faça UMA pergunta por vez, exatamente como definida no roteiro.
- Não improvise perguntas fora do roteiro.
- Se o participante desviar, redirecione gentilmente para a pergunta atual.
- Seja cordial e conciso (máximo 3 frases por resposta).
- Nunca revele o conteúdo futuro do roteiro.
- Responda APENAS com a mensagem a enviar ao participante, sem explicações extras.
"""

_NODE_INSTRUCTION = """\

---
[INSTRUÇÃO INTERNA — NÃO EXIBIR AO PARTICIPANTE]
Nó atual: {node_key} (tipo: {node_type})
Texto do nó: {node_text}
{next_info}
Envie exatamente o texto do nó acima ao participante agora.
"""


class PromptBuilder:
    """
    Constrói o payload de mensagens para a Anthropic Messages API.

    Parâmetros
    ----------
    objective : str
        Objetivo do ResearchScript (preenchido no system prompt).
    max_history : int
        Número máximo de pares (user+assistant) do histórico a incluir.
        Mantém o contexto controlado e evita exceder o context window.
    """

    def __init__(self, objective: str, max_history: int = 10) -> None:
        self._objective = objective
        self._max_history = max_history

    def build(
        self,
        *,
        history: list[dict[str, str]],
        current_node: ScriptNode,
        inbound_text: str | None,
    ) -> dict[str, Any]:
        """
        Monta o payload completo.

        Parameters
        ----------
        history : list[dict]
            Lista de dicts {"role": "user"|"assistant", "content": str}
            ordenada da mais antiga para a mais recente.
        current_node : ScriptNode
            Nó atual do roteiro.
        inbound_text : str | None
            Texto recebido do contato na mensagem atual.

        Returns
        -------
        dict com "system" e "messages" prontos para a API Anthropic.
        """
        system_prompt = _SYSTEM_TEMPLATE.format(objective=self._objective)

        # Truncar histórico
        trimmed = self._trim_history(history)

        # Instrução do nó atual
        next_info = (
            f"Próximo nó: {current_node.next_key}"
            if current_node.next_key
            else "Este é o último nó — encerre a conversa com cordialidade."
        )
        node_instruction = _NODE_INSTRUCTION.format(
            node_key=current_node.key,
            node_type=current_node.node_type,
            node_text=current_node.text,
            next_info=next_info,
        )

        # Última mensagem do usuário
        user_content = (inbound_text or "") + node_instruction

        messages: list[dict[str, str]] = list(trimmed)
        messages.append({"role": "user", "content": user_content})

        logger.debug(
            "[PromptBuilder] node=%s history_len=%d",
            current_node.key,
            len(trimmed),
        )

        return {
            "system": system_prompt,
            "messages": messages,
        }

    def _trim_history(
        self, history: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """
        Mantém no máximo max_history pares (user + assistant).
        Garante que o histórico sempre comece com um turno 'user'.
        """
        # Filtrar apenas user/assistant
        valid = [m for m in history if m.get("role") in ("user", "assistant")]

        # Pegar os últimos max_history * 2 turnos (pares)
        limit = self._max_history * 2
        trimmed = valid[-limit:] if len(valid) > limit else valid

        # Garantir que começa com "user"
        while trimmed and trimmed[0]["role"] != "user":
            trimmed = trimmed[1:]

        return trimmed

    @staticmethod
    def history_from_messages(messages: list[Any]) -> list[dict[str, str]]:
        """
        Converte lista de objetos Message (ORM) em formato de histórico.

        Aceita tanto objetos com atributos .direction/.raw_text quanto dicts.
        """
        result: list[dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, dict):
                direction = msg.get("direction", "inbound")
                text = msg.get("raw_text") or ""
            else:
                direction = getattr(msg, "direction", "inbound")
                text = getattr(msg, "raw_text", "") or ""

            role = "user" if direction == "inbound" else "assistant"
            if text:
                result.append({"role": role, "content": text})
        return result
