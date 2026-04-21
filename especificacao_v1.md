# Especificação v1 — Instagram Research Agent

## Decisões aprovadas
- Não basear o produto em contato livre com todos os seguidores.
- Basear o produto em interações oficiais e consentidas.
- Construir solução própria.
- Usar Meta oficial + backend próprio + Postgres + IA.
- Usar PRD + Event Storming + C4 + ADR + OpenAPI.
- Fazer uma rodada forte de especificação e depois ajustar só por delta.

## Visão do produto
Aplicação para conduzir conversas via Instagram com usuários que interagiram com uma conta, usando IA para qualificação, pesquisa e coleta estruturada de dados, com persistência em PostgreSQL e painel analítico para acompanhamento de resultados.

## Objetivo do negócio
- Coletar dados qualitativos e quantitativos via conversa.
- Qualificar leads/respondentes.
- Identificar padrões, dores, perfil e intenção.
- Aumentar taxa de resposta e profundidade da entrevista.
- Manter histórico unificado por usuário.

## Escopo do MVP
- Uma conta de Instagram conectada.
- Ingestão de eventos oficiais.
- Criação de perfil do contato.
- Motor de conversa com roteiro guiado.
- IA para resposta controlada.
- Extração estruturada de atributos.
- Persistência em PostgreSQL.
- Painel operacional básico.
- Dashboard analítico inicial.
- Handoff para humano.
- Trilhas mínimas de auditoria e consentimento.

## Fora de escopo do MVP
- Outreach em massa para seguidores sem gatilho oficial.
- Multi-tenant complexo.
- Billing interno.
- Omnichannel completo.
- Fine-tuning de modelo próprio.
- Social listening amplo fora do fluxo conversacional.

## Requisitos funcionais principais
1. Receber eventos oficiais do Instagram.
2. Identificar ou criar contato.
3. Criar e manter conversas.
4. Registrar mensagens recebidas e enviadas.
5. Gerenciar consentimento.
6. Selecionar roteiro de pesquisa.
7. Orquestrar a próxima ação.
8. Gerar resposta com IA.
9. Extrair dados estruturados.
10. Classificar o contato.
11. Escalonar para humano quando necessário.
12. Permitir revisão humana.
13. Exibir painel operacional.
14. Gerar relatórios e dashboards.
15. Versionar roteiros e prompts.
16. Registrar auditoria.

## Requisitos não funcionais principais
- Compliance com LGPD e políticas do canal oficial.
- Observabilidade e rastreamento.
- Idempotência no processamento de eventos.
- Segurança de acesso e dados.
- Escalabilidade moderada para o MVP.
- Retenção e descarte configuráveis.
- Score de confiança para extrações.

## Event Storming resumido
### Atores
- Respondente
- Instagram/Meta
- Webhook Receiver
- Orquestrador de Conversa
- Motor de IA
- Extrator de Dados
- Operador Humano
- Administrador

### Eventos de domínio
- interacao_recebida
- contato_identificado
- contato_criado
- conversa_iniciada
- mensagem_recebida
- consentimento_registrado
- roteiro_associado
- proxima_acao_calculada
- resposta_ia_gerada
- mensagem_enviada
- atributo_extraido
- classificacao_atualizada
- baixa_confianca_detectada
- handoff_criado
- resposta_revisada_por_humano
- conversa_encerrada
- auditoria_registrada

## Arquitetura resumida
### Containers
- Webhook Receiver
- Conversation Service
- AI Orchestrator
- Extraction & Classification Service
- PostgreSQL
- Redis
- Admin/Operations UI
- Analytics Layer

### ADRs iniciais
1. Usar integração oficial da Meta/Instagram.
2. Usar PostgreSQL como fonte principal de verdade.
3. Habilitar `pgvector` de forma opcional.
4. Usar IA para geração e extração estruturada.
5. Manter handoff humano nativo.
6. Versionar prompts e roteiros.

## Máquina de estados da conversa

```text
[EVENTO RECEBIDO]
      |
      v
   [OPEN]
      |
      v
   [ACTIVE]
    / |  \
   /  |   \
  v   v    v
[WAITING] [IN_HANDOFF] [CLOSED]
   |         |
   v         v
[ACTIVE]   [ACTIVE/CLOSED]
   |
   v
[ABANDONED]
```

### Transições válidas
- OPEN → ACTIVE
- ACTIVE → WAITING
- ACTIVE → IN_HANDOFF
- ACTIVE → CLOSED
- ACTIVE → ABANDONED
- WAITING → ACTIVE
- WAITING → ABANDONED
- IN_HANDOFF → ACTIVE
- IN_HANDOFF → CLOSED
- CLOSED → OPEN (nova interação futura)
- ABANDONED → OPEN (nova interação futura)

## Organização recomendada no projeto Abacus
Arquivos a manter no projeto:
- `ddl_v1.sql`
- `openapi_v1.yaml`
- `backlog_v1.md`
- `prompts_v1.md`
- `especificacao_v1.md`

## Regra de economia de créditos
- Sempre referenciar os arquivos já enviados no projeto.
- Pedir alterações só por delta.
- Evitar repetir o contexto completo.
- Separar conversas por módulo.
- Usar o Agent só quando entrar em implementação real.
