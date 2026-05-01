"""
app/services/evolution_outbound.py
Envia mensagens outbound via Evolution API v2.3.7.

Endpoint
--------
POST http://{EVOLUTION_BASE_URL}/message/sendText/{instance}
Header: apikey: {EVOLUTION_API_KEY}
Body:   {"number": "5561999990000", "text": "mensagem"}

Configuração via variáveis de ambiente
---------------------------------------
    EVOLUTION_BASE_URL   : URL base da Evolution API  (ex: http://localhost:8080)
    EVOLUTION_API_KEY    : chave de autenticação
    EVOLUTION_INSTANCE   : nome da instância           (ex: Provedor_CRM)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10.0  # segundos


class OutboundError(RuntimeError):
    """Falha no envio de mensagem outbound."""


class EvolutionOutboundClient:
    """
    Envia mensagem de texto via Evolution API.

    Parameters
    ----------
    base_url : str
        URL base da Evolution API (sem barra final).
    api_key : str
        Chave de autenticação (header 'apikey').
    instance : str
        Nome da instância Evolution.
    timeout : float
        Timeout em segundos para a requisição HTTP.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        instance: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = (base_url or os.environ.get("EVOLUTION_BASE_URL", "http://localhost:8080")).rstrip("/")
        self._api_key = api_key or os.environ.get("EVOLUTION_API_KEY", "")
        self._instance = instance or os.environ.get("EVOLUTION_INSTANCE", "Provedor_CRM")
        self._timeout = timeout

        if not self._api_key:
            raise OutboundError(
                "EVOLUTION_API_KEY não definida. Defina a variável de ambiente ou passe api_key ao construtor."
            )

    def send_text(self, *, number: str, text: str) -> dict[str, Any]:
        """
        Envia mensagem de texto para um número WhatsApp.

        Parameters
        ----------
        number : str
            Número no formato E.164 sem '+' (ex: "5561999990000").
        text : str
            Texto da mensagem.

        Returns
        -------
        dict — resposta JSON da Evolution API.

        Raises
        ------
        OutboundError
            Em qualquer falha HTTP ou de conexão.
        """
        url = f"{self._base_url}/message/sendText/{self._instance}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self._api_key,
        }
        body = {"number": number, "text": text}

        logger.info(
            "[Outbound] Enviando mensagem → number=%s instance=%s",
            number,
            self._instance,
        )

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, headers=headers, json=body)
        except httpx.TimeoutException as exc:
            raise OutboundError(f"Timeout ao enviar mensagem para Evolution API: {exc}") from exc
        except httpx.RequestError as exc:
            raise OutboundError(f"Erro de conexão com Evolution API: {exc}") from exc

        if response.status_code not in (200, 201):
            raise OutboundError(f"Evolution API retornou status {response.status_code}: {response.text[:200]}")

        logger.info(
            "[Outbound] Mensagem enviada com sucesso → status=%d number=%s",
            response.status_code,
            number,
        )
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}
