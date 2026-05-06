# Ambiente de Desenvolvimento - Fase 1

## Pré-requisitos
- Docker Desktop instalado e rodando
- Git

## Subir o ambiente
  ash
git clone https://github.com/geterborges100-tech/agente-pesquisa.git
cd agente-pesquisa
copy .env.example .env   # preencher EVOLUTION_API_KEY, OPENROUTER_API_KEY, etc.
docker compose up -d --build
docker compose logs -f api
  

## Verificar saúde
  ash
curl http://localhost:8001/health
  

## Testar webhook local

### Usando PowerShell
  powershell
.\local\test_webhook.ps1 -Mensagem "Olá" -Telefone "5561999990000"
  

### Usando curl (Git Bash / WSL)
  ash
curl -X POST http://localhost:8001/webhooks/evolution/whatsapp \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976" \
  -d @- <<'EOF'
{
  "event": "messages.upsert",
  "instance": "Provedor_CRM",
  "data": {
    "key": {
      "remoteJid": "5561999990000@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-001"
    },
    "message": {"conversation": "Olá"},
    "pushName": "Teste",
    "messageTimestamp": 1713312000
  }
}
EOF
  

## Endpoints implementados na Fase 1

- POST /webhooks/evolution/whatsapp – recebe mensagens do WhatsApp
- GET /health – verifica se o serviço está no ar
- GET /contacts – lista contatos
- GET /contacts/{id} – detalha um contato
- GET /conversations – lista conversas
- GET /conversations/{id} – detalha uma conversa
- GET /conversations/{id}/messages – lista mensagens de uma conversa
- POST /conversations/{id}/close – encerra uma conversa

## Fluxo completo da Fase 1

1. **Inbound webhook** – Evolution API envia payload messages.upsert
2. **Validação e idempotência** – verifica assinatura e evita duplicatas
3. **Contato** – cria ou recupera contato pelo external_user_id
4. **Conversa** – cria ou recupera conversa aberta
5. **Mensagem inbound** – persiste mensagem recebida
6. **Roteiro ativo** – carrega um ResearchScript com status "active"
7. **Contexto mínimo** – PromptBuilder monta histórico truncado
8. **Chamada LLM** – LLMClient envia prompt ao OpenRouter (Gemini)
9. **Outbound** – resposta é enviada via Evolution API e persistida
10. **Testes** – 20 testes unitários + 1 E2E cobrindo o fluxo feliz

## Para fases futuras (fora do MVP da Fase 1)

- Painel administrativo completo
- Handoff humano e fila operacional
- Múltiplas instâncias e canais
- Métricas e dashboard analítico
- RBAC e multi-tenant
- Classificações avançadas e extração estruturada
- Retenção e auditoria configuráveis

