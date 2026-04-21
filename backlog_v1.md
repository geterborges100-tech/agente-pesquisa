# Backlog por Sprints — Instagram Research Agent

## Sprint 0 — Setup e Fundação
- Repositório e estrutura de projeto
- Docker Compose: Postgres + Redis + backend
- Migrations iniciais com `ddl_v1.sql`
- Configuração de variáveis de ambiente
- Autenticação básica do painel interno (JWT)
- CI/CD mínimo: lint + test + build
- Configuração do app Meta/Instagram Developer
- Registro do webhook e verificação de token

## Sprint 1 — Ingestão e Contatos
- `POST /webhooks/meta/instagram` para receber e validar evento
- Idempotência por `external_event_id`
- Persistência de evento bruto na tabela `events`
- Resolver ou criar contato a partir do evento
- Criar conversa associada ao contato
- Registrar mensagem inbound
- Audit log de criação de contato e conversa
- Testes unitários do fluxo de ingestão

## Sprint 2 — Motor de Conversa e IA
- Máquina de estados da conversa (`OPEN → ACTIVE → CLOSED`)
- Carregamento de roteiro e versão ativa
- Seleção do próximo nó do roteiro
- `PromptBuilder` para montar contexto do LLM
- Integração com provedor de LLM
- `GuardrailValidator` antes do envio
- Envio de mensagem outbound via Meta API
- Registro de mensagem outbound com `prompt_version_id`
- Testes de integração ponta a ponta

## Sprint 3 — Extração e Classificação
- `AnswerParser` para associar resposta ao nó do roteiro
- `AttributeExtractor` para extrair atributos estruturados
- `ConfidenceScorer` para score de confiança
- Persistência em `answers` e `extracted_attributes`
- `Classifier` para atualizar `segment`, `tags` e `lead_score`
- Fila de revisão para baixa confiança
- `PATCH /answers/{id}` para revisão humana
- `PATCH /attributes/{id}` para correção de atributo

## Sprint 4 — Handoff e Painel Operacional
- Detecção automática de gatilhos de handoff
- `POST /conversations/{id}/handoff`
- Transição para `IN_HANDOFF`
- Painel operacional: lista de conversas com status
- Painel operacional: detalhe de conversa + mensagens
- Painel operacional: fila de handoffs pendentes
- `POST /conversations/{id}/messages/send` para envio manual
- `POST /conversations/{id}/close` para encerramento manual
- Notificação interna básica de novo handoff

## Sprint 5 — Consentimento, Auditoria e Compliance
- Fluxo de registro de consentimento na conversa
- Tabela `consents` populada corretamente
- `audit_logs` em ações críticas
- Política de retenção configurável
- Validação de LGPD: evitar coleta sensível sem base legal
- Documentação mínima de compliance

## Sprint 6 — Métricas e Dashboard
- `GET /metrics/overview`
- `GET /metrics/conversations`
- `GET /metrics/research`
- Integração com Metabase
- Dashboards iniciais:
  - conversas por status
  - taxa de conclusão
  - taxa de handoff
  - distribuição de segmentos
  - qualidade de extração
- Exportação CSV básica

## Sprint 7 — Estabilização e MVP Release
- Testes end-to-end do fluxo completo
- Revisão de segurança: autenticação, tokens, criptografia
- Revisão de idempotência e resiliência
- Documentação da API com Swagger UI
- Runbook operacional básico
- Deploy em produção
- Monitoramento básico com alertas
- Validação com usuário real em conta de teste
