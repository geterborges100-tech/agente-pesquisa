import json
import subprocess
import time
import uuid

BASE_URL = "http://localhost:8001/webhooks/evolution/whatsapp"
APIKEY = "B6D711FCDE4D4FD5936544120E713976"


def send_webhook(payload):
    """Envia um payload via curl.exe e retorna a resposta como dict."""
    body = json.dumps(payload)
    result = subprocess.run(
        [
            "curl.exe",
            "-s",
            "-X",
            "POST",
            BASE_URL,
            "-H",
            "Content-Type: application/json",
            "-H",
            f"apikey: {APIKEY}",
            "-d",
            body,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_e2e_flow_new_contact():
    """Fluxo feliz completo: novo contato -> consentimento -> IA -> outbound"""
    uid = str(uuid.uuid4())[:8]
    phone = f"556199999{uid[-4:]}"
    base_payload = {
        "event": "messages.upsert",
        "instance": "Provedor_CRM",
        "data": {
            "key": {"remoteJid": f"{phone}@s.whatsapp.net", "fromMe": False, "id": f"E2E-{uid}-001"},
            "message": {"conversation": "Olá, quero participar"},
            "pushName": "TesteE2E",
            "messageTimestamp": 1713312000,
        },
    }

    # 1. Primeira mensagem
    resp = send_webhook(base_payload)
    assert resp["status"] == "awaiting_consent", f"Step 1 failed: {resp}"

    # 2. Envia "Sim"
    base_payload["data"]["key"]["id"] = f"E2E-{uid}-002"
    base_payload["data"]["message"]["conversation"] = "Sim"
    resp = send_webhook(base_payload)
    assert resp["status"] == "processed", f"Step 2 failed: {resp}"

    # 3. Mensagem pós-consentimento
    time.sleep(1)
    base_payload["data"]["key"]["id"] = f"E2E-{uid}-003"
    base_payload["data"]["message"]["conversation"] = "Qual é a capital do Brasil?"
    resp = send_webhook(base_payload)
    assert resp["status"] == "processed", f"Step 3 failed: {resp}"

    # 4. Verifica persistência outbound
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "C:\\ia\\agente-pesquisa\\docker-compose.yml",
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "agent",
            "-d",
            "research_agent",
            "-c",
            f"SELECT direction FROM messages WHERE contact_id = (SELECT id FROM contacts WHERE external_user_id='{phone}') AND direction = 'outbound' LIMIT 1;",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "outbound" in result.stdout, f"Outbound not persisted: {result.stdout}"
