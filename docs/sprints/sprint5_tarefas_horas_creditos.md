# Sprint 5 — Tarefas Executáveis com Horas e Estimativa de Créditos Abacus

## Projeto
**Agente de Pesquisa Instagram/WhatsApp**

## Contexto atual
- Sprint 4 concluída;
- Sprint 5 em andamento;
- objetivo do Sprint 5: ativar e endurecer o fluxo com LLM real, consentimento e auditoria mínima confiável.

## Premissas
1. O desenvolvimento diário usará Gemini rápido como ferramenta padrão.
2. O Abacus AI Agent será usado apenas se houver bloqueio real ou tarefa estrutural.
3. As estimativas de créditos abaixo são aproximadas.
4. Os créditos exatos variam conforme o uso.
5. O acompanhamento final deve ser feito na página de perfil/créditos do ChatLLM Teams.

## Base do Sprint 5
Já concluído:
- `models_v1.py` atualizado com `Consent` + `AuditLog`;
- `consent_repository.py` criado;
- `audit_service.py` criado e corrigido;
- `guardrail_validator.py` criado;
- `ContactRepository` restaurado;
- imports OK;
- container estável.

Pendências confirmadas:
- aplicar consent gate em `evolution_webhook_service_fixed.py`;
- criar migration Alembic para `consents` + `audit_logs`;
- executar teste E2E.

## Objetivo deste documento
Transformar o Sprint 5 em tarefas pequenas, sequenciais e executáveis, com:
- objetivo;
- escopo;
- arquivos principais;
- critério de aceite;
- estimativa de horas;
- estimativa de créditos do Abacus;
- recomendação de uso de ferramenta.

## Visão geral do Sprint 5
- **Sprint 5.1** — Mapeamento e contrato técnico do consent gate
- **Sprint 5.2** — Implementação do consent gate no webhook
- **Sprint 5.3** — Migration Alembic de `consents` e `audit_logs`
- **Sprint 5.4** — Validação de persistência e integridade básica
- **Sprint 5.5** — Teste E2E sem consentimento
- **Sprint 5.6** — Teste E2E com consentimento válido
- **Sprint 5.7** — Hardening leve, logs e fechamento do sprint

## Estimativa total do Sprint 5
**Tempo total estimado:**
- cenário econômico e fluido: **10h a 15h**
- cenário realista recomendado: **14h a 22h**
- cenário com bloqueios e retrabalho: **20h a 30h**

**Créditos Abacus estimados:**
- cenário super econômico: **500 a 1.500 créditos**
- cenário equilibrado recomendado: **1.200 a 3.000 créditos**
- cenário com escalonamento mais frequente: **2.500 a 5.000 créditos**

## Tarefa 5.1 — Mapeamento e contrato técnico do consent gate
**Objetivo:** definir exatamente onde o consentimento será validado, em qual ordem, e qual o comportamento quando não houver consentimento válido.

**Escopo:**
- revisar o fluxo atual do webhook;
- confirmar o ponto da checagem;
- definir o comportamento de bloqueio;
- definir como auditar esse bloqueio.

**Arquivos principais:**
- `evolution_webhook_service_fixed.py`
- `consent_repository.py`
- `guardrail_validator.py`
- `audit_service.py`

**Critério de aceite:** existe uma definição curta e sem ambiguidade de:
- ponto da checagem;
- condição de bloqueio;
- condição de continuação;
- evento de auditoria.

**Estimativa de horas:** **0,75h a 1,5h**

**Estimativa de créditos:**
- Gemini rápido / chat curto: **20 a 80**
- recomendação: **não usar Abacus AI Agent aqui**

**Ferramenta recomendada:** Gemini rápido + ChatLLM para consolidar.

## Tarefa 5.2 — Implementação do consent gate no webhook
**Objetivo:** aplicar a regra de consentimento dentro do fluxo principal do webhook.

**Escopo:**
- inserir a checagem no ponto certo;
- impedir chamada ao LLM quando não houver consentimento válido;
- impedir saída livre quando houver bloqueio;
- registrar auditoria mínima.

**Arquivos principais:**
- `evolution_webhook_service_fixed.py`
- `consent_repository.py`
- `guardrail_validator.py`
- `audit_service.py`

**Critério de aceite:**
- sem consentimento válido, o fluxo é bloqueado antes do LLM;
- com consentimento válido, o fluxo segue normalmente;
- o bloqueio deixa registro auditável.

**Estimativa de horas:** **2h a 4h**

**Estimativa de créditos:**
- usando Gemini rápido e revisão curta: **80 a 250**
- com 1 escalonamento pontual para Abacus AI Agent: **400 a 1.000**

**Ferramenta recomendada:** Gemini rápido primeiro. Escalar só se surgir regressão real.

## Tarefa 5.3 — Migration Alembic de `consents` e `audit_logs`
**Objetivo:** persistir no banco as estruturas necessárias para consentimento e auditoria.

**Escopo:**
- criar migration Alembic;
- validar schema final;
- garantir compatibilidade com models e repositories.

**Arquivos principais:**
- diretório de migrations Alembic;
- `models_v1.py` ou equivalente;
- pontos de leitura/escrita relacionados.

**Critério de aceite:**
- migration aplica sem erro;
- tabelas existem;
- nomes e campos essenciais estão coerentes com o código existente.

**Estimativa de horas:** **1,5h a 3h**

**Estimativa de créditos:**
- usando Gemini rápido: **50 a 180**
- com revisão mais forte no chat: **80 a 220**
- com escalonamento para AI Agent: **400 a 900**

## Tarefa 5.4 — Validação de persistência e integridade básica
**Objetivo:** confirmar que o fluxo consegue ler e gravar consentimento e auditoria sem quebrar o container ou os serviços.

**Escopo:**
- subir ambiente;
- aplicar migration;
- validar leitura/gravação mínima;
- revisar logs essenciais.

**Critério de aceite:**
- ambiente sobe;
- migration roda;
- leitura/gravação básica funciona;
- não há erro estrutural nos logs principais.

**Estimativa de horas:** **1h a 2h**

**Estimativa de créditos:**
- uso baixo com Gemini rápido para triagem: **30 a 120**
- recomendação: não usar AI Agent salvo bloqueio confuso de integração.

## Tarefa 5.5 — Teste E2E sem consentimento
**Objetivo:** provar que o sistema bloqueia corretamente quando não há consentimento válido.

**Escopo:**
- disparar cenário sem consentimento;
- validar que não chama LLM no fluxo esperado;
- validar registro de auditoria ou log de bloqueio.

**Critério de aceite:**
- payload sem consentimento resulta em bloqueio consistente;
- o sistema não segue para resposta livre;
- há sinal observável do bloqueio.

**Estimativa de horas:** **1,5h a 3h**

**Estimativa de créditos:**
- Gemini rápido para roteiro de teste e leitura de falha: **50 a 180**
- se usar AI Agent: **400 a 900**

## Tarefa 5.6 — Teste E2E com consentimento válido
**Objetivo:** provar que o sistema continua o fluxo normalmente quando há consentimento válido.

**Escopo:**
- disparar cenário com consentimento válido;
- validar passagem pelo fluxo correto;
- validar que o comportamento esperado continua funcionando.

**Critério de aceite:**
- payload com consentimento segue o fluxo principal;
- não há bloqueio indevido;
- o comportamento final está coerente com o sprint.

**Estimativa de horas:** **1,5h a 3h**

**Estimativa de créditos:**
- Gemini rápido e revisão curta: **50 a 180**
- com escalonamento: **400 a 900**

## Tarefa 5.7 — Hardening leve, logs e fechamento do sprint
**Objetivo:** fazer uma revisão curta de robustez, limpar arestas principais e fechar o sprint com checkpoint confiável.

**Escopo:**
- revisar logs importantes;
- revisar mensagens de erro principais;
- confirmar pendências restantes;
- registrar checkpoint do sprint.

**Critério de aceite:**
- sprint termina com estado estável;
- pendências residuais ficam listadas;
- existe checkpoint claro para o próximo sprint.

**Estimativa de horas:** **1h a 2,5h**

**Estimativa de créditos:**
- Gemini rápido para resumo e checklist: **30 a 120**
- normalmente não precisa AI Agent.

## Ordem recomendada de execução

### Dia 1
- 5.1 Mapeamento e contrato técnico
- 5.2 Implementação do consent gate

### Dia 2
- 5.3 Migration Alembic
- 5.4 Validação de persistência

### Dia 3
- 5.5 E2E sem consentimento
- 5.6 E2E com consentimento válido
- 5.7 Hardening e fechamento

Se houver menos disponibilidade diária, dividir em **4 a 5 dias**.

## Capacidade recomendada
Com **4 a 6 horas líquidas por dia**, o Sprint 5 pode ser fechado em:
- **3 a 5 dias úteis**, dependendo do retrabalho.

## Estimativa consolidada de créditos por tarefa
- **5.1:** 20 a 80
- **5.2:** 80 a 250, ou 400 a 1.000 se escalar
- **5.3:** 50 a 180, ou 400 a 900 se escalar
- **5.4:** 30 a 120
- **5.5:** 50 a 180, ou 400 a 900 se escalar
- **5.6:** 50 a 180, ou 400 a 900 se escalar
- **5.7:** 30 a 120

## Total consolidado recomendado
### Sem uso relevante do Abacus AI Agent
- **310 a 1.110 créditos**

### Com 1 a 2 escalonamentos pontuais ao AI Agent
- **1.200 a 3.000 créditos**

### Com uso excessivo e pouco disciplinado do AI Agent
- **2.500 a 5.000 créditos**

## Estratégia recomendada de créditos para o Sprint 5
Estratégia ideal:
- usar Gemini rápido para planejamento, patch inicial, revisão de log e desenho de teste;
- reservar Abacus AI Agent apenas para uma destas situações:
  1. regressão estrutural após aplicar o consent gate;
  2. conflito entre migration e fluxo real;
  3. E2E quebrando em múltiplas camadas sem causa clara após 20 a 30 minutos de investigação boa.

### Meta saudável de consumo
- teto alvo: **até 1.500 créditos**
- teto aceitável: **até 3.000 créditos**
- acima disso: revisar o método, porque provavelmente houve uso excessivo do AI Agent ou prompts amplos demais.

## Recomendação de organização no GitHub
### Pode ir para o repositório
- `metodo_oficial_desenvolvimento_abacus.md`
- `checklist_operacional_diario_com_horas.md`
- `sprint5_tarefas_horas_creditos.md`

### Organização sugerida
```text
docs/
  processo/
    metodo_oficial_desenvolvimento.md
    checklist_operacional_diario.md
  sprints/
    sprint5_tarefas_horas_creditos.md
```

## Melhor formato: TXT ou MD?
Para GitHub, prefira **`.md`** porque:
- renderiza melhor;
- organiza melhor títulos e listas;
- melhora leitura no navegador;
- facilita navegação do time.

Use `.txt` apenas para rascunho rápido ou arquivo pessoal fora do repositório.

## Próximo passo recomendado
1. converter os 3 arquivos principais para Markdown;
2. organizar em `docs/processo/` e `docs/sprints/`;
3. commitar junto com o fechamento do Sprint 5 ou no início do Sprint 6.

**Sugestão de commit:**
`docs: add development method, daily checklist and sprint 5 execution plan`
