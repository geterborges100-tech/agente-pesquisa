from __future__ import annotations

import logging
from typing import Any

from app.services.script_loader import ScriptNode

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATE = """\
Você é um assistente de pesquisa de mercado conversacional e educado.
Seu objetivo é coletar respostas dos participantes de forma natural e empática.
Se o participante não quiser responder a uma pergunta, aceite a recusa e passe para o próximo tópico.
Nunca insista na mesma pergunta se o participante já recusou.
Mantenha um diálogo fluido e agradável.
Responda APENAS com a mensagem a enviar ao participante, sem explicações extras.
"""


class PromptBuilder:
    def __init__(self, objective: str = "Pesquisa de mercado", max_history: int = 10) -> None:
        self._objective = objective
        self._max_history = max_history

    def build(
        self,
        *,
        history: list[dict[str, str]] = None,
        current_node: ScriptNode | None = None,
        inbound_text: str | None = None,
    ) -> dict[str, Any]:
        system_prompt = _SYSTEM_TEMPLATE
        trimmed = self._trim_history(history or [])

        if current_node:
            next_info = (
                f"Próximo nó: {current_node.next_key}"
                if current_node.next_key
                else "Último nó — encerre com cordialidade."
            )
            node_instruction = f"\n\n---\n[INSTRUÇÃO INTERNA — NÃO EXIBIR AO PARTICIPANTE]\nNó atual: {current_node.key} (tipo: {current_node.node_type})\nTexto do nó: {current_node.text}\n{next_info}\nEnvie exatamente o texto do nó acima ao participante agora."
            user_content = (inbound_text or "") + node_instruction
            messages = list(trimmed) + [{"role": "user", "content": user_content}]
        else:
            # Modo livre com histórico
            messages = list(trimmed)
            if inbound_text:
                messages.append({"role": "user", "content": inbound_text})

        return {"system": system_prompt, "messages": messages}

    def _trim_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        valid = [m for m in history if m.get("role") in ("user", "assistant")]
        limit = self._max_history * 2
        trimmed = valid[-limit:] if len(valid) > limit else valid
        while trimmed and trimmed[0]["role"] != "user":
            trimmed = trimmed[1:]
        return trimmed

    @staticmethod
    def history_from_messages(messages: list[Any]) -> list[dict[str, str]]:
        result = []
        for msg in messages:
            direction = getattr(msg, "direction", "inbound")
            text = getattr(msg, "raw_text", "") or ""
            role = "user" if direction == "inbound" else "assistant"
            if text:
                result.append({"role": role, "content": text})
        return result
