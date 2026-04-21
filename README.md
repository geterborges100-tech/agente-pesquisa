# Agente de Pesquisa - Instagram/WhatsApp

Projeto FastAPI para processar webhooks da Evolution API, manter estado de conversa e gerar respostas com LLM via OpenRouter.

## Objetivo atual

- Fluxo oficial: Inbound -> Conversation Service -> AI Engine -> Prompt Builder -> OpenRouter (Gemini) -> Outbound Evolution API.
- Reduzir custo cognitivo e custo de tokens.
- Manter o núcleo vivo enxuto e previsível.

## Componentes principais

- `main.py`: entrada da aplicação e roteamento.
- `evolution_webhook_service_fixed.py`: processamento de webhooks.
- `conversation_service.py`: histórico e estado.
- `ai_engine.py`: orquestração da IA.
- `prompt_builder.py`: montagem do contexto para o LLM.
- `llm_client.py`: cliente OpenRouter.
- `script_loader.py`: carregamento de fluxos dinâmicos.

## Como subir

1. Ajustar variáveis no `.env`.
2. Subir a stack com Docker Compose.
3. Verificar o container `research_agent_api`.

Exemplo:

```bash
cd /home/ubuntu/agente-pesquisa
docker compose up -d --force-recreate
```

## Como testar

- Validar o webhook de entrada.
- Conferir logs do container da API.
- Verificar se a resposta sai pela Evolution API.
- Rodar testes unitários dos módulos críticos quando necessário.

## Deploy

- Usar branch de trabalho para mudanças grandes.
- Criar checkpoint Git antes de refatorações relevantes.
- Após alterar código ou `.env`, reiniciar com `docker compose up -d --force-recreate`.

## Variáveis de ambiente relevantes

- `ACCOUNT_ID`
- `EVOLUTION_BASE_URL`
- `OPENROUTER_API_KEY`
- `LLM_MODEL`

## Regra de economia

- Manter histórico curto.
- Evitar chamar o LLM sem necessidade.
- Não carregar documentação legada no fluxo principal.
