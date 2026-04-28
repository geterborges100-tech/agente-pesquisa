#!/bin/bash
# Script de teste do consent gate - Agente de Pesquisa
# Uso: ./test_webhook.sh "mensagem" [nome_contato] [wa_id]

MENSAGEM="${1:-Olá}"
NOME="${2:-Contato Teste}"
WA_ID="${3:-5561999990000}"
TIMESTAMP=$(date +%s)
ID="TEST-${TIMESTAMP}"

echo "========================================"
echo "🚀 Disparando webhook de teste"
echo "========================================"
echo "ID:       $ID"
echo "Contato:  $NOME"
echo "WhatsApp: $WA_ID"
echo "Mensagem: $MENSAGEM"
echo "========================================"
echo ""
echo "📤 Resposta da API:"
echo "----------------------------------------"

curl -s -X POST http://localhost:8001/webhooks/evolution/whatsapp \
  -H "Content-Type: application/json" \
  -H "apikey: ${EVOLUTION_API_KEY}" \
  -d "{
    \"event\": \"messages.upsert\",
    \"instance\": \"Provedor_CRM\",
    \"data\": {
      \"key\": {
        \"remoteJid\": \"${WA_ID}@s.whatsapp.net\",
        \"fromMe\": false,
        \"id\": \"${ID}\"
      },
      \"message\": {\"conversation\": \"${MENSAGEM}\"},
      \"pushName\": \"${NOME}\",
      \"messageTimestamp\": ${TIMESTAMP}
    }
  }" | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo "✅ Teste concluído - ID: $ID"
echo ""
echo "📋 Para ver os logs:"
echo "   docker compose logs api --tail=20"
echo "========================================"
