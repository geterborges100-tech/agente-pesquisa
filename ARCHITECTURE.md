# Arquitetura do Sistema - Agente de Pesquisa

Documento técnico simplificado focado no "Núcleo Vivo" (Sprint 5).

## 1. Fluxo E2E

1. **Inbound**: Evolution API -> Webhook -> `webhooks_router.py` -> `evolution_webhook_service_fixed.py`.
2. **Contexto**: `conversation_service.py` recupera histórico e estado atual do banco PostgreSQL.
3. **Core**: `ai_engine.py` orquestra o nó atual do roteiro via `script_loader.py`.
4. **Prompt**: `prompt_builder.py` gera o payload (JSON) com histórico truncado (max 5 pares).
5. **LLM**: `llm_client.py` chama OpenRouter (`google/gemini-2.0-flash-001`).
6. **Outbound**: `evolution_outbound.py` envia a resposta final para o usuário.

## 2. Estados da Conversa

- **STARTING**: contato detectado, disparando o primeiro nó do roteiro.
- **ACTIVE**: conversa fluindo, IA interpretando respostas e avançando nós.
- **PAUSED**: aguardando intervenção manual (opcional).
- **CLOSED**: roteiro finalizado ou tempo limite excedido.

## 3. Núcleo Vivo

- `main.py`
- `evolution_webhook_service_fixed.py`
- `conversation_service.py`
- `ai_engine.py`
- `prompt_builder.py`
- `llm_client.py`
- `script_loader.py`

## 4. Estratégia de Deploy

- **Infra**: Docker Compose no servidor Oracle.
- **Git**: branch funcional para mudanças relevantes.
- **Persistência**: PostgreSQL 15.

Este documento existe para evitar releitura de relatórios antigos e reduzir custo cognitivo.
