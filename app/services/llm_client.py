"""
app/services/llm_client.py
Integração com qualquer provedor OpenAI-compatible (OpenRouter, OpenAI, etc.).

Configuração via banco de dados (tabela llm_configs) — sem hardcode de chaves.
Modelo padrão atual: google/gemini-2.0-flash-001 via OpenRouter.

Para trocar de modelo: atualizar llm_configs no banco e reiniciar o container.
"""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Erro na chamada ao LLM."""


class LLMClient:
    """
    Cliente OpenAI-compatible — funciona com OpenRouter, OpenAI, Anthropic (via compat), etc.

    Parameters
    ----------
    api_key   : chave de API do provedor
    base_url  : URL base da API, ex: "https://openrouter.ai/api/v1"
    model     : identificador do modelo, ex: "google/gemini-2.0-flash-001"
    max_tokens: limite de tokens na resposta
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        max_tokens: int = 512,
    ) -> None:
        if not api_key:
            raise LLMError("api_key não pode ser vazia.")
        if not base_url:
            raise LLMError("base_url não pode ser vazia.")
        if not model:
            raise LLMError("model não pode ser vazio.")

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, prompt_payload: dict[str, Any]) -> str:
        """
        Envia o payload para a API e retorna o texto da resposta.

        Parameters
        ----------
        prompt_payload : dict
            Saída do PromptBuilder.build() — chaves "system" e "messages".

        Returns
        -------
        str — texto gerado pelo modelo.

        Raises
        ------
        LLMError em qualquer falha da API.
        """
        system = prompt_payload.get("system", "")
        messages = prompt_payload.get("messages", [])

        if not messages:
            raise LLMError("prompt_payload não contém 'messages'.")

        # Injeta system prompt como primeira mensagem de sistema
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=full_messages,  # type: ignore[arg-type]
            )
        except APIConnectionError as exc:
            raise LLMError(f"Falha de conexão com a API: {exc}") from exc
        except RateLimitError as exc:
            raise LLMError(f"Rate limit atingido: {exc}") from exc
        except APIStatusError as exc:
            raise LLMError(
                f"API retornou status {exc.status_code}: {exc.message}"
            ) from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMError("API retornou resposta sem conteúdo.")

        result = content.strip()
        logger.info(
            "[LLMClient] model=%s tokens_used=%s",
            self._model,
            response.usage.completion_tokens if response.usage else "?",
        )
        return result