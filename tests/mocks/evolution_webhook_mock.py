"""
Mock do webhook da Evolution API para testes locais.
Dispensa ngrok durante o desenvolvimento.
"""

import pytest
from httpx import AsyncClient

BASE_WEBHOOK_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "Provedor_CRM",
    "data": {
        "key": {"remoteJid": "5561999990000@s.whatsapp.net", "fromMe": False, "id": "TEST-LOCAL-MOCK"},
        "message": {"conversation": "Olá, quero participar da pesquisa"},
        "pushName": "Teste Mock",
        "messageTimestamp": 1713312000,
    },
}


@pytest.fixture
def webhook_payload():
    """Retorna uma cópia limpa do payload base."""
    return BASE_WEBHOOK_PAYLOAD.copy()


@pytest.fixture
def evolution_headers():
    """Headers esperados pela Evolution API."""
    return {"apikey": "B6D711FCDE4D4FD5936544120E713976", "ngrok-skip-browser-warning": "true"}


@pytest.mark.asyncio
async def test_webhook_recebe_mensagem_texto(webhook_payload, evolution_headers):
    """Simula uma mensagem de texto enviada pelo WhatsApp."""
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.post("/webhooks/evolution/whatsapp", json=webhook_payload, headers=evolution_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("awaiting_consent", "processed", "skipped")


@pytest.mark.asyncio
async def test_webhook_recebe_mensagem_audio(webhook_payload, evolution_headers):
    """Simula uma mensagem de áudio (sem texto)."""
    payload = webhook_payload.copy()
    payload["data"]["message"] = {"audio": {"url": "https://exemplo.com/audio.ogg"}}
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.post("/webhooks/evolution/whatsapp", json=payload, headers=evolution_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_recebe_mensagem_imagem(webhook_payload, evolution_headers):
    """Simula uma mensagem de imagem com legenda."""
    payload = webhook_payload.copy()
    payload["data"]["message"] = {"imageMessage": {"caption": "Foto de teste"}}
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.post("/webhooks/evolution/whatsapp", json=payload, headers=evolution_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_evento_conexao(evolution_headers):
    """Simula um evento de status/conexão (não processa mensagem)."""
    payload = {"event": "connection.update", "instance": "Provedor_CRM", "data": {"status": "connected"}}
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.post("/webhooks/evolution/whatsapp", json=payload, headers=evolution_headers)
    assert response.status_code == 400  # Só processa messages.upsert
