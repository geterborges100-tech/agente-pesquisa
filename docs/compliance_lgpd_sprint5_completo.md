# Artefato 1 — Matriz de Consentimento

> Sistema: Agente de Pesquisa - Instagram | Sprint 5 | Compliance LGPD

---

| Momento | Ação | Onde registrar | Se negar | Base legal LGPD | Art. |
|---|---|---|---|---|---|
| **Primeiro contato** (estado `OPEN`) | `pedir` | `consents` — `type=initial`, `status=pending` | Encerrar conversa imediatamente. Enviar mensagem de encerramento. Não processar nenhum dado além do identificador de canal. | Consentimento | 7º, I |
| **Início de pesquisa** (estado `ACTIVE`) | `registrar` | `consents` — `type=research_participation`, `status=granted` | Bloquear coleta de respostas. Manter conversa aberta apenas para encerramento voluntário. | Consentimento / Legítimo interesse se B2B | 7º, I / IX |
| **Coleta de dado pessoal** (nome, e-mail, telefone) | `registrar` | `consents` — `type=personal_data`, `data_type=[campo]`, `status=granted` | Não persistir o campo. Continuar fluxo sem o dado. Registrar recusa no `audit_log`. | Consentimento ou Execução de contrato | 7º, I / V |
| **Coleta de dado sensível** (saúde, religião, etnia, orientação) | `bloquear` | Não registrar em `consents`. Registrar tentativa no `audit_log` com criticidade `ALTA`. | N/A — coleta bloqueada por guardrail antes de chegar ao usuário. | Consentimento específico e destacado obrigatório. Sem base legal alternativa admissível neste contexto. | 11, I |
| **Encerramento** (estado `CLOSED`) | `registrar` | `consents` — `type=data_retention`, `status=granted/denied` | Anonimizar ou deletar dados conforme política de retenção. Manter apenas `audit_logs` de consentimento. | Consentimento para retenção pós-pesquisa | 7º, I |
| **Handoff para humano** (estado `IN_HANDOFF`) | `pedir` | `consents` — `type=human_handoff`, `status=pending→granted/denied` | Cancelar handoff. Manter atendimento automatizado ou encerrar conforme preferência do usuário. Notificar operador humano da recusa. | Consentimento — compartilhamento com terceiro exige nova base | 7º, I; 5º, VII |

---

## Observações de implementação

- O campo `type` na tabela `consents` deve usar enum fixo: `initial | research_participation | personal_data | sensitive_data | human_handoff | data_retention`.
- O campo `status` deve ter transições controladas: `pending → granted | denied`. Revogação exige novo registro — nunca update — para preservar histórico imutável.
- Dado sensível **nunca chega ao fluxo de consentimento do usuário**: o guardrail deve interceptar no `prompt_builder.py` ou `ai_engine.py`, antes de gerar a pergunta. O registro vai direto para `audit_log`, não para `consents`.
- Na negação de handoff, o operador humano não deve ter acesso ao histórico da conversa sem consentimento prévio — compartilhamento com terceiro (art. 5º, VII LGPD).
-e 

---

# Artefato 2 — Matriz de Auditoria

> Sistema: Agente de Pesquisa - Instagram | Sprint 5 | Compliance LGPD

---

| Ação crítica | Evento de domínio | Campos mínimos do `audit_log` | Criticidade | Retenção do log |
|---|---|---|---|---|
| **Criação de contato** | `contact.created` | `actor=system`, `entity=contact`, `entity_id=contact_id`, `action=create`, `timestamp`, `instagram_id` (hash), `channel` | Médio | 2 anos |
| **Início de conversa** | `conversation.started` | `actor=system`, `entity=conversation`, `entity_id=conversation_id`, `action=start`, `timestamp`, `contact_id`, `state=OPEN` | Médio | 2 anos |
| **Registro de consentimento** | `consent.granted` | `actor=contact`, `entity=consent`, `entity_id=consent_id`, `action=grant`, `timestamp`, `conversation_id`, `consent_type`, `channel_message_id` | **Alto** | **Indeterminado** — não deletar |
| **Negação de consentimento** | `consent.denied` | `actor=contact`, `entity=consent`, `entity_id=consent_id`, `action=deny`, `timestamp`, `conversation_id`, `consent_type`, `channel_message_id` | **Alto** | **Indeterminado** — não deletar |
| **Chamada ao LLM** | `llm.request_sent` | `actor=system`, `entity=llm_call`, `entity_id=request_uuid`, `action=request`, `timestamp`, `conversation_id`, `model`, `prompt_tokens`, `response_tokens` | Baixo | 90 dias |
| **Envio de mensagem outbound** | `message.sent_outbound` | `actor=system`, `entity=message`, `entity_id=message_id`, `action=send`, `timestamp`, `conversation_id`, `channel_message_id`, `recipient_id` (hash) | Baixo | 1 ano |
| **Handoff criado** | `handoff.created` | `actor=system`, `entity=handoff`, `entity_id=handoff_id`, `action=create`, `timestamp`, `conversation_id`, `reason`, `operator_id` | **Alto** | 2 anos |
| **Encerramento de conversa** | `conversation.closed` | `actor=system|contact`, `entity=conversation`, `entity_id=conversation_id`, `action=close`, `timestamp`, `final_state`, `close_reason` | Médio | 2 anos |
| **Tentativa de coleta de dado sensível bloqueada** | `guardrail.sensitive_data_blocked` | `actor=system`, `entity=guardrail`, `entity_id=request_uuid`, `action=block`, `timestamp`, `conversation_id`, `data_category` (sem valor), `rule_triggered` | **Alto** | **Indeterminado** — não deletar |

---

## Schema mínimo do `audit_log`

```sql
CREATE TABLE audit_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event         VARCHAR(64) NOT NULL,          -- ex: consent.granted
    actor         VARCHAR(32) NOT NULL,          -- system | contact | operator
    entity        VARCHAR(32) NOT NULL,          -- contact | conversation | consent | ...
    entity_id     UUID NOT NULL,
    action        VARCHAR(32) NOT NULL,          -- create | grant | deny | block | send | ...
    criticality   VARCHAR(8) NOT NULL,           -- alto | medio | baixo
    conversation_id UUID,
    context       JSONB,                         -- campos adicionais (model, tokens, reason, etc.)
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Regras de implementação

- **Imutabilidade**: `audit_log` é append-only. Nenhum registro deve ser atualizado ou deletado por fluxo de aplicação. Exclusão apenas via job de retenção com permissão restrita.
- **`data_category` em bloqueios**: registrar a categoria do dado (ex: `health`, `religion`) mas **nunca o valor** que o LLM tentou coletar.
- **`actor=contact`**: usar hash do `instagram_id`, nunca o ID em claro, para minimizar exposição em logs.
- **Logs de criticidade Alta com retenção indeterminada**: `consent.granted`, `consent.denied` e `guardrail.sensitive_data_blocked` não devem ter prazo de expiração — são evidência de compliance.
- **`context` como JSONB**: permite adicionar campos situacionais sem alterar schema. Validar no nível da aplicação, não do banco.
-e 

---

# Artefato 3 — Política de Retenção

> Sistema: Agente de Pesquisa - Instagram | Sprint 5 | Compliance LGPD

---

## Parte 1 — Tabela de Retenção por Tipo de Dado

| Tipo de dado | Tabela(s) | Prazo padrão | Ação ao expirar | Observação |
|---|---|---|---|---|
| **Mensagens da conversa** | `messages` | 1 ano após encerramento | Deletar conteúdo (`body = NULL`), manter metadados (`id`, `conversation_id`, `created_at`, `direction`) | Corpo da mensagem é dado pessoal; metadados são operacionais |
| **Dados do contato** | `contacts` | 2 anos após último contato | Anonimizar: `name = 'ANONIMIZADO'`, `instagram_id = hash irreversível`, demais campos `NULL` | Não deletar o registro — FK de outras tabelas depende do `contact_id` |
| **Atributos extraídos** | `contact_attributes` | 1 ano após coleta | Deletar linha inteira | Atributos derivados de LLM não têm valor operacional pós-pesquisa |
| **Respostas do participante** | `conversation_responses` | 1 ano após encerramento da pesquisa | Arquivar em storage frio (S3/object storage) com criptografia, deletar da tabela principal | Podem ter valor analítico agregado; arquivar antes de deletar |
| **Logs de auditoria — criticidade baixa/média** | `audit_logs` | 2 anos | Deletar linha inteira | Inclui: `llm.request_sent`, `message.sent_outbound`, `conversation.started/closed`, `contact.created` |
| **Logs de auditoria — criticidade alta** | `audit_logs` | **Indeterminado — nunca deletar** | Nenhuma | Inclui: `consent.granted`, `consent.denied`, `guardrail.sensitive_data_blocked`, `handoff.created` |
| **Registros de consentimento** | `consents` | **Indeterminado — nunca deletar** | Nenhuma | Evidência de base legal. Exigível pela ANPD. Manter mesmo após exclusão de dados do titular. |
| **Histórico de handoff** | `handoffs` | 2 anos após encerramento | Anonimizar `operator_id` e `contact_id` (substituir por hash), manter estrutura e timestamps | Histórico operacional; identidade do operador não precisa ser preservada |

---

## Parte 2 — Configuração de Prazos

### Estratégia: tabela de configuração no banco + variáveis de ambiente como fallback

**Tabela `retention_policies`** (fonte primária):

```sql
CREATE TABLE retention_policies (
    id           SERIAL PRIMARY KEY,
    data_type    VARCHAR(64) UNIQUE NOT NULL,  -- ex: messages, contacts, audit_logs_low
    retention_days INT,                         -- NULL = indeterminado (nunca expirar)
    action       VARCHAR(16) NOT NULL,          -- delete | anonymize | archive
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by   VARCHAR(64)                    -- rastreabilidade de quem alterou
);
```

**Variáveis de ambiente** (fallback se tabela não encontrada ou inacessível):

```env
RETENTION_MESSAGES_DAYS=365
RETENTION_CONTACTS_DAYS=730
RETENTION_ATTRIBUTES_DAYS=365
RETENTION_RESPONSES_DAYS=365
RETENTION_AUDIT_LOW_DAYS=730
RETENTION_AUDIT_HIGH_DAYS=0        # 0 = indeterminado
RETENTION_CONSENTS_DAYS=0          # 0 = indeterminado
RETENTION_HANDOFFS_DAYS=730
```

**Lógica de resolução no código:**

```python
def get_retention_days(data_type: str) -> int | None:
    policy = db.query(RetentionPolicy).filter_by(data_type=data_type).first()
    if policy:
        return policy.retention_days  # None = nunca expirar
    days = int(os.getenv(f"RETENTION_{data_type.upper()}_DAYS", 365))
    return days if days > 0 else None
```

---

## Parte 3 — Regra de Prioridade em Conflito

**Cenário de conflito**: dado pessoal expirou (ex: corpo de mensagem, 1 ano), mas o `audit_log` referenciando aquela mensagem ainda está dentro do prazo de retenção (2 anos).

**Regra:**

```
Dado pessoal SEMPRE expira no seu próprio prazo,
independentemente do prazo do audit_log que o referencia.
```

Ordem de prioridade:

1. **Registros de consentimento** — retenção indeterminada, nunca sobrescritos por nenhuma outra regra.
2. **Audit logs de criticidade alta** — retenção indeterminada, nunca sobrescritos.
3. **Dados pessoais** — expiram no prazo próprio, mesmo que audit_logs ainda existam.
4. **Audit logs de criticidade baixa/média** — expiram no prazo próprio.
5. **Dados operacionais** (metadados, estrutura de conversa) — expiram por último.

**Implementação prática**: o `audit_log` não deve armazenar o valor do dado pessoal — apenas referência (`entity_id`). Quando o dado expira e é anonimizado/deletado, o log mantém apenas o ID da entidade, que se torna uma referência opaca. Isso resolve o conflito sem violar nenhum dos dois prazos.

---

## Parte 4 — O que NÃO deve ser deletado mesmo após expiração

Os itens abaixo são **imunes a qualquer job de retenção** e devem ser protegidos por permissão de banco restrita (ex: role `retention_job` sem `DELETE` nestas tabelas):

| Item | Motivo | Tabela |
|---|---|---|
| Registros de `consent.granted` | Prova de base legal para coleta | `audit_logs` + `consents` |
| Registros de `consent.denied` | Prova de respeito à recusa | `audit_logs` + `consents` |
| Registros de `guardrail.sensitive_data_blocked` | Prova de que dado sensível não foi coletado | `audit_logs` |
| Registros de `handoff.created` | Prova de que compartilhamento com terceiro foi rastreado | `audit_logs` |
| Estrutura da tabela `consents` (linhas inteiras) | Exigível pela ANPD em fiscalização | `consents` |

**Mecanismo de proteção sugerido:**

```sql
-- Role do job de retenção não tem DELETE em tabelas protegidas
REVOKE DELETE ON audit_logs FROM retention_job;
REVOKE DELETE ON consents FROM retention_job;

-- Job só opera nas tabelas permitidas
GRANT DELETE ON messages, contact_attributes, conversation_responses TO retention_job;
GRANT UPDATE ON contacts, handoffs TO retention_job;  -- para anonimização
```

---

## Job de retenção — estrutura mínima

```python
# Executar via cron diário (ex: 02:00 UTC)
def run_retention_job():
    expire_message_bodies()          # DELETE body WHERE encerrado > 1 ano
    anonymize_expired_contacts()     # UPDATE contacts SET name=... WHERE último contato > 2 anos
    delete_expired_attributes()      # DELETE contact_attributes WHERE coletado > 1 ano
    archive_expired_responses()      # COPY TO S3 + DELETE WHERE pesquisa > 1 ano
    delete_low_audit_logs()          # DELETE audit_logs WHERE criticidade != 'alto' AND > 2 anos
    anonymize_expired_handoffs()     # UPDATE handoffs SET operator_id=hash WHERE > 2 anos
    # consents e audit_logs alto: NUNCA tocados por este job
```
-e 

---

# Artefato 4 — Checklist LGPD + Casos de Teste

> Sistema: Agente de Pesquisa - Instagram | Sprint 5 | Compliance LGPD

---

## Parte A — Checklist LGPD

| # | Item de compliance | Como validar no código | Risco se não implementado |
|---|---|---|---|
| 1 | **Coleta com base legal declarada** | Toda inserção em `consents` deve ter `legal_basis` preenchido com enum fixo (`consent`, `contract`, `legitimate_interest`). Validar via constraint de banco + Pydantic model. | Coleta ilícita — art. 7º LGPD. Multa de até 2% do faturamento (art. 52). |
| 2 | **Dado sensível sem base legal bloqueado** | Guardrail no `prompt_builder.py` com lista de categorias proibidas. Teste unitário com prompts sintéticos contendo termos de saúde, religião, etnia, orientação sexual. | Infração gravíssima — art. 11 LGPD. Dado sensível coletado sem base legal específica invalida toda a pesquisa. |
| 3 | **Direito de acesso** | Endpoint `GET /contacts/{id}/data-export` que retorna todos os dados do titular em JSON. Deve incluir: mensagens, atributos, respostas, consentimentos. | Violação do art. 18, II LGPD. Titular pode acionar ANPD em até 15 dias após pedido não atendido. |
| 4 | **Direito de exclusão** | Endpoint `DELETE /contacts/{id}` que aciona `run_erasure_flow()`: anonimiza contato, deleta mensagens, atributos e respostas. Não deleta `consents` nem `audit_logs`. | Violação do art. 18, VI LGPD. |
| 5 | **Consentimento explícito e registrado** | Verificar antes de cada coleta se existe registro em `consents` com `status=granted` para o `consent_type` correspondente. Sem registro → bloquear. | Coleta sem consentimento — art. 7º, I. Todo dado coletado sem base é ilícito e deve ser deletado. |
| 6 | **Finalidade declarada** | Campo `purpose` obrigatório na tabela `consents`. Validar que o `purpose` registrado corresponde ao uso real do dado (ex: `research_response` não pode ser usado para marketing). | Desvio de finalidade — art. 6º, I. Uso incompatível com finalidade declarada é infração autônoma. |
| 7 | **Minimização de dados** | Revisar `prompt_builder.py`: o prompt enviado ao LLM deve conter apenas os campos estritamente necessários para a pergunta atual. Nenhum histórico completo de atributos deve ser injetado por padrão. | Coleta excessiva — art. 6º, III. Dado coletado além da necessidade tem base legal questionável. |
| 8 | **Segurança de acesso** | `instagram_id` armazenado como hash irreversível. Conexão ao banco via SSL obrigatório (`sslmode=require`). Variáveis sensíveis apenas em `.env` — nunca em código ou logs. Role de banco segregada por função (`app_user`, `retention_job`, `readonly`). | Violação de segurança — art. 46 LGPD. Incidente de vazamento exige notificação à ANPD em 72h (art. 48). |

---

## Parte B — Casos de Teste

---

### CT-01 — Usuário aceita consentimento → conversa continua

| Campo | Detalhe |
|---|---|
| **Cenário** | Usuário em estado `OPEN` recebe mensagem de consentimento e responde afirmativamente |
| **Entrada** | Webhook com `body = "sim"` (ou variação: "aceito", "concordo", "s") após envio da mensagem de consentimento |
| **Comportamento esperado** | 1. `consents` recebe linha com `status=granted`, `consent_type=initial`. 2. `audit_log` registra `consent.granted`. 3. Estado da conversa transita para `ACTIVE`. 4. LLM é acionado para próxima mensagem. |
| **Comportamento proibido** | Conversa avançar para `ACTIVE` sem registro em `consents`. LLM ser chamado antes da confirmação do consentimento. |

---

### CT-02 — Usuário nega consentimento → conversa encerra com mensagem adequada

| Campo | Detalhe |
|---|---|
| **Cenário** | Usuário em estado `OPEN` recebe mensagem de consentimento e responde negativamente |
| **Entrada** | Webhook com `body = "não"` (ou variação: "nao", "recuso", "n") após envio da mensagem de consentimento |
| **Comportamento esperado** | 1. `consents` recebe linha com `status=denied`, `consent_type=initial`. 2. `audit_log` registra `consent.denied`. 3. Sistema envia mensagem de encerramento cordial via Evolution API. 4. Estado transita para `CLOSED`. 5. Nenhum dado além do `instagram_id` (hash) e timestamps é persistido. |
| **Comportamento proibido** | Continuar fluxo de pesquisa após negação. Chamar LLM. Persistir nome, atributos ou respostas. Enviar outra mensagem pedindo reconsideração. |

---

### CT-03 — LLM tenta coletar dado sensível → guardrail bloqueia

| Campo | Detalhe |
|---|---|
| **Cenário** | Durante geração de prompt, o contexto da pesquisa induz o LLM a formular pergunta sobre dado sensível |
| **Entrada** | Resposta do LLM contendo pergunta sobre saúde, religião, etnia ou orientação sexual (ex: "Você tem alguma condição de saúde?") |
| **Comportamento esperado** | 1. Guardrail no `ai_engine.py` ou `prompt_builder.py` detecta categoria sensível na resposta do LLM. 2. Mensagem é descartada — não enviada ao usuário. 3. `audit_log` registra `guardrail.sensitive_data_blocked` com `data_category` (sem o valor). 4. Sistema envia mensagem neutra de fallback ou avança para próxima pergunta do script. |
| **Comportamento proibido** | Entregar ao usuário qualquer pergunta sobre dado sensível. Registrar o valor do dado em qualquer tabela. Silenciar o bloqueio sem registrar no `audit_log`. |

---

### CT-04 — Evento duplicado chega → idempotência garante não registrar duas vezes

| Campo | Detalhe |
|---|---|
| **Cenário** | Evolution API entrega o mesmo webhook duas vezes (retry de rede) |
| **Entrada** | Dois webhooks idênticos com mesmo `message_id` do Instagram em intervalo < 5s |
| **Comportamento esperado** | 1. Primeira entrega processada normalmente. 2. Segunda entrega detectada como duplicata via `channel_message_id` já existente. 3. Segunda entrega descartada silenciosamente — sem nova linha em `messages`, `consents` ou `audit_logs`. 4. Resposta HTTP 200 retornada para a Evolution API em ambos os casos. |
| **Comportamento proibido** | Registrar dois consentimentos para o mesmo evento. Enviar duas respostas ao usuário. Retornar erro 5xx que cause novo retry. |

---

### CT-05 — Handoff criado → audit_log registrado corretamente

| Campo | Detalhe |
|---|---|
| **Cenário** | Sistema decide escalar conversa para operador humano |
| **Entrada** | Trigger interno de handoff (ex: usuário solicitou falar com humano, ou LLM atingiu limite de tentativas) |
| **Comportamento esperado** | 1. Registro criado em `handoffs` com `conversation_id`, `reason`, `operator_id`. 2. `audit_log` registra `handoff.created` com criticidade `alto`. 3. `consents` recebe pedido de consentimento `type=human_handoff, status=pending`. 4. Estado da conversa transita para `IN_HANDOFF`. |
| **Comportamento proibido** | Criar handoff sem registrar em `audit_log`. Compartilhar histórico da conversa com operador antes de consentimento concedido. Avançar para handoff sem registro em `handoffs`. |

---

### CT-06 — Dado de contato expira → anonimização executada

| Campo | Detalhe |
|---|---|
| **Cenário** | Job de retenção diário encontra contato cujo último contato foi há mais de 2 anos |
| **Entrada** | Registro em `contacts` com `last_contact_at < NOW() - INTERVAL '2 years'` |
| **Comportamento esperado** | 1. `name` substituído por `'ANONIMIZADO'`. 2. `instagram_id` substituído por hash irreversível (se ainda não era hash). 3. Demais campos pessoais (`email`, `phone`, etc.) setados para `NULL`. 4. `audit_log` registra `contact.anonymized` com `entity_id=contact_id`. 5. Registro em `contacts` mantido (FK preservation). |
| **Comportamento proibido** | Deletar a linha de `contacts` (quebra FKs). Anonimizar `consents` ou `audit_logs` associados. Executar anonimização sem registrar em `audit_log`. |

---

### CT-07 — Usuário solicita exclusão dos dados → fluxo de exclusão ativado

| Campo | Detalhe |
|---|---|
| **Cenário** | Titular envia pedido de exclusão de dados (art. 18, VI LGPD) via canal configurado |
| **Entrada** | Requisição `DELETE /contacts/{contact_id}` com autenticação válida |
| **Comportamento esperado** | 1. `messages.body` deletado para todas as mensagens do contato. 2. `contact_attributes` deletados. 3. `conversation_responses` deletadas. 4. `contacts` anonimizado (não deletado). 5. `consents` e `audit_logs` preservados integralmente. 6. `audit_log` registra `contact.erasure_requested` e `contact.erased` com timestamp. 7. Resposta ao solicitante em até 15 dias (registrar prazo). |
| **Comportamento proibido** | Deletar `consents` ou `audit_logs`. Deletar a linha de `contacts`. Executar exclusão sem registrar em `audit_log`. Ignorar ou atrasar pedido além de 15 dias. |

---

### CT-08 — Mensagem vazia recebida → LLM não é chamado

| Campo | Detalhe |
|---|---|
| **Cenário** | Evolution API entrega webhook com corpo de mensagem vazio ou apenas whitespace |
| **Entrada** | Webhook com `body = ""` ou `body = "   "` |
| **Comportamento esperado** | 1. `evolution_webhook_service_fixed.py` detecta mensagem vazia antes de qualquer processamento. 2. Mensagem descartada — não inserida em `messages`. 3. LLM não é chamado. 4. Nenhum `audit_log` gerado (evento não é crítico). 5. HTTP 200 retornado para Evolution API. |
| **Comportamento proibido** | Chamar LLM com prompt vazio ou malformado. Inserir linha vazia em `messages`. Gerar erro 5xx. Avançar estado da conversa. |
