# Guia DeepSeek — Fase 1 + Resumo Executivo do Projeto

## 1. Resumo Executivo do Projeto Completo

### Visão Geral

Propõe-se o desenvolvimento de um **Agente de Pesquisa Inteligente** capaz de conduzir interações automatizadas com usuários, coletar dados estruturados e operar em canais digitais com possibilidade de evolução operacional.

A solução foi concebida para começar com um **MVP funcional**, focado no fluxo principal de atendimento e coleta de dados, e evoluir gradualmente para uma plataforma mais completa com operação assistida, handoff para humano, configuração avançada, métricas e governança.

O objetivo de negócio é:

- coletar dados qualitativos e quantitativos via conversa
- qualificar leads ou respondentes
- identificar padrões, dores, perfil e intenção
- manter histórico unificado por usuário
- permitir evolução controlada da operação

### Direcionamento Estratégico

A proposta não se limita a um chatbot simples. O projeto caminha para uma **plataforma de pesquisa conversacional**, inspirada em boas práticas de ferramentas pagas de mercado, mas implementada de forma enxuta e progressiva.

### Recursos e Práticas Inspirados em Ferramentas de Mercado

Para enriquecer a solução, a proposta considera recursos comuns em plataformas como Zendesk, Intercom e soluções omnichannel:

- gestão centralizada de conversas
- histórico consolidado por contato
- roteamento operacional evolutivo
- configuração de fluxos e roteiros
- uso de IA com comportamento controlado
- trilhas de auditoria
- métricas operacionais e analíticas
- possibilidade de transbordo para atendimento humano

### Etapas de Entrega ao Cliente

#### Fase 1 — Fundação do Agente

**Objetivo:** entregar o fluxo mínimo funcional ponta a ponta.

**Entregas:**

- recebimento de eventos inbound
- criação e atualização de contatos
- abertura e continuidade de conversas
- execução de roteiro básico
- resposta automatizada com IA
- persistência de mensagens e dados principais
- testes básicos do fluxo principal

**Estimativa:** 30 a 50 horas

#### Fase 2 — Estrutura Operacional

**Objetivo:** preparar a base para operação com maior controle.

**Entregas:**

- cadastro de agentes
- configuração de instâncias/canais
- vínculo entre agentes e operação
- base para roteamento futuro

**Estimativa:** 60 a 90 horas

#### Fase 3 — Handoff e Operação Assistida

**Objetivo:** permitir interação entre automação e atendimento humano.

**Entregas:**

- handoff para humano
- fila operacional
- painel mínimo de acompanhamento
- envio manual de mensagens

**Estimativa:** 70 a 100 horas

#### Fase 4 — Configuração Avançada e IA

**Objetivo:** dar maior flexibilidade ao comportamento do agente.

**Entregas:**

- configuração de modelos de IA
- personalização de comportamento e tom
- múltiplos roteiros
- regras de fallback

**Estimativa:** 50 a 80 horas

#### Fase 5 — Métricas, Monitoramento e Governança

**Objetivo:** oferecer visibilidade da operação e capacidade de controle.

**Entregas:**

- dashboard de métricas
- indicadores por conversa, agente e roteiro
- exportação de dados
- auditoria e retenção

**Estimativa:** 60 a 90 horas

#### Fase 6 — Refinamento e Preparação para Escala

**Objetivo:** estabilizar e preparar para uso contínuo.

**Entregas:**

- ajustes de performance
- refinamento operacional
- testes ponta a ponta
- documentação final
- preparação para produção

**Estimativa:** 40 a 60 horas

### Resumo Consolidado de Esforço

| Fase | Horas estimadas |
|---|---:|
| Fase 1 | 30 a 50h |
| Fase 2 | 60 a 90h |
| Fase 3 | 70 a 100h |
| Fase 4 | 50 a 80h |
| Fase 5 | 60 a 90h |
| Fase 6 | 40 a 60h |
| **Total** | **310 a 470h** |

### Conclusão Executiva

O projeto deve ser conduzido em etapas, priorizando entregas curtas e funcionais. A melhor estratégia é começar com um núcleo operacional mínimo e expandir apenas após validação do fluxo principal. Isso reduz risco, acelera a entrega de valor e evita desperdício de desenvolvimento.

## 2. Premissas para Continuidade com DeepSeek

Este guia foi elaborado para orientar a continuidade do projeto com foco máximo em produtividade.

Foram consideradas:

- as especificações já existentes no repositório
- a arquitetura e backlog já definidos
- a decisão registrada no ADR sobre automação do fluxo de desenvolvimento
- as ferramentas já instaladas e aceitas no projeto

### Ferramentas já instaladas e que devem ser aproveitadas

Conforme a decisão arquitetural registrada, o projeto já conta com ferramentas que reduzem retrabalho:

- **Ruff + pre-commit** para lint e formatação
- **pytest + GitHub Actions** para testes automáticos
- **Makefile** para centralizar comandos
- **Aider** para edição assistida com contexto Git
- **mypy** previsto para uso futuro, sem ser prioridade agora

### Regra principal de produtividade

A orientação para o DeepSeek é simples:

**não expandir escopo além da Fase 1 e reutilizar ao máximo o que já existe.**

## 3. Escopo exato da Fase 1

A Fase 1 deve entregar um **MVP funcional ponta a ponta**, sem entrar ainda em painéis completos, handoff humano, múltiplos canais avançados, múltiplos agentes, métricas reais ou omnichannel completo.

### Resultado esperado da Fase 1

Ao final desta fase, o sistema deve ser capaz de:

1. receber um evento inbound do canal já suportado
2. validar e registrar o evento com idempotência
3. resolver ou criar o contato
4. criar ou recuperar a conversa
5. registrar a mensagem inbound
6. carregar um roteiro ativo
7. montar o contexto mínimo para IA
8. gerar uma resposta controlada
9. enviar ou simular o envio outbound
10. persistir o outbound
11. validar o fluxo com testes básicos

## 4. O que não fazer agora

Para reduzir tempo e evitar desperdício, o DeepSeek **não deve** implementar nesta etapa:

- painel administrativo completo
- múltiplos canais novos
- múltiplas instâncias
- multiagente completo
- handoff humano completo
- fila operacional robusta
- dashboard analítico real
- RBAC completo
- multi-tenant
- refatorações amplas sem necessidade
- classificações avançadas e automações complexas

A regra é:

**fechar primeiro o fluxo feliz completo antes de expandir escopo.**

## 5. Estratégia de desenvolvimento mais produtiva

### Princípios

1. não redesenhar a arquitetura
2. seguir o que já está no repositório
3. completar o que está mais próximo de funcionar
4. testar a cada bloco pequeno
5. priorizar o happy path
6. postergar edge cases não críticos

### Estratégia técnica recomendada

Trabalhar por uma única fatia vertical:

**webhook → contato → conversa → mensagem inbound → roteiro → IA → outbound → persistência → testes**

Essa abordagem reduz retrabalho e acelera a validação.

## 6. Arquivos de referência prioritários

O DeepSeek deve começar pelos arquivos mais relevantes já existentes no repositório:

- `README.md`
- `ARCHITECTURE.md`
- `backlog_v1.md`
- `especificacao_v1.md`
- `app/main.py`
- `app/routers/conversations.py`
- `app/routers/contacts.py`
- `app/routers/research_scripts.py`
- `app/schemas/schemas.py`
- `app/models/extended_models.py`
- `tests/`
- `test_webhook.sh`
- `test_body.json`
- `ADR-001-ferramentas-automacao.md`

## 7. Passo a passo para o DeepSeek continuar a Fase 1

### Etapa 0 — Confirmar definição de pronto

**Objetivo:** alinhar exatamente o que será considerado concluído.

**Checklist de pronto:**

- webhook funcional
- persistência do evento inbound
- criação ou resolução de contato
- criação ou recuperação de conversa
- registro da mensagem inbound
- seleção de roteiro ativo
- montagem do contexto mínimo
- chamada de LLM funcional
- persistência da resposta outbound
- teste automatizado do fluxo principal

**Estimativa:** 1 a 2 horas

### Etapa 1 — Fazer leitura rápida e mapear gaps reais

**Objetivo:** entender o que já está pronto, o que está parcial e o que falta.

**Saída esperada:** lista curta com três grupos:

- pronto
- parcial
- falta implementar

**Regra:** essa leitura deve ser curta e objetiva.

**Estimativa:** 2 a 3 horas

### Etapa 2 — Fechar o fluxo de ingestão inbound

**Objetivo:** garantir que o sistema receba e persista corretamente a entrada.

**Escopo mínimo:**

- recebimento do evento inbound
- validação básica do payload
- idempotência por identificador externo
- persistência do evento bruto
- resolução ou criação do contato
- criação ou recuperação da conversa
- registro da mensagem inbound

**Estimativa:** 6 a 10 horas

### Etapa 3 — Fechar o fluxo mínimo de conversa

**Objetivo:** garantir que a conversa avance com estado mínimo e roteiro básico.

**Escopo mínimo:**

- estado mínimo da conversa
- vínculo com contato
- carregamento de um roteiro ativo
- seleção simples do próximo passo
- continuidade mínima de contexto

**Estimativa:** 5 a 8 horas

### Etapa 4 — Integrar o trecho mínimo de IA

**Objetivo:** fechar o ciclo automatizado de resposta.

**Escopo mínimo:**

- montagem do contexto mínimo para prompt
- chamada ao cliente de LLM já previsto no projeto
- validação básica antes do envio
- geração de resposta objetiva
- persistência da mensagem outbound

**Estimativa:** 5 a 8 horas

### Etapa 5 — Registrar resposta estruturada no nível mínimo viável

**Objetivo:** garantir coleta estruturada mínima sem entrar em classificações avançadas.

**Escopo mínimo:**

- registrar resposta por conversa
- vincular resposta à mensagem
- vincular resposta ao passo do roteiro
- manter formato evolutivo para fases futuras

**Estimativa:** 3 a 5 horas

### Etapa 6 — Criar testes automáticos do fluxo feliz

**Objetivo:** garantir estabilidade e evolução segura.

**Cobertura mínima sugerida:**

1. evento inbound válido
2. idempotência de evento repetido
3. criação de contato
4. criação de conversa
5. registro da mensagem inbound
6. geração de outbound
7. persistência do outbound

**Ferramentas a usar:**

- `pytest`
- `GitHub Actions`
- `Ruff`
- `pre-commit`
- `Makefile`

**Estimativa:** 6 a 10 horas

### Etapa 7 — Ajustes finais e documentação curta de uso

**Objetivo:** deixar a fase utilizável sem perder tempo com documentação extensa.

**Entregas:**

- instrução de subida do ambiente
- como testar o webhook
- quais endpoints já funcionam
- qual fluxo a Fase 1 cobre
- o que ficou para fases seguintes

**Estimativa:** 2 a 4 horas

## 8. Estimativa consolidada da Fase 1

| Etapa | Horas |
|---|---:|
| Etapa 0 — Definição de pronto | 1 a 2h |
| Etapa 1 — Leitura e gap analysis | 2 a 3h |
| Etapa 2 — Ingestão inbound | 6 a 10h |
| Etapa 3 — Fluxo mínimo de conversa | 5 a 8h |
| Etapa 4 — Integração mínima de IA | 5 a 8h |
| Etapa 5 — Registro estruturado mínimo | 3 a 5h |
| Etapa 6 — Testes automatizados | 6 a 10h |
| Etapa 7 — Documentação curta | 2 a 4h |
| **Total da Fase 1** | **30 a 50h** |

### Faixa mais realista para execução produtiva

Considerando o que já existe no repositório, a faixa mais realista é:

**34 a 42 horas**

## 9. Ordem ideal de execução

Para gastar o menor tempo possível, seguir esta ordem:

1. confirmar definição de pronto
2. mapear gaps reais
3. fechar inbound
4. fechar conversa
5. fechar IA
6. persistir resposta estruturada mínima
7. escrever testes
8. documentar

## 10. Como usar as ferramentas já instaladas para economizar tempo

### Ruff + pre-commit

Usar desde o início para evitar retrabalho com erros simples.

Comando recomendado:

```bash
make check
```

### pytest + GitHub Actions

Tudo que for concluído na Fase 1 deve ter ao menos teste do happy path.

### Makefile

Usar como ponto único de execução para reduzir carga cognitiva.

### Aider

Usar para mudanças pequenas e objetivas, especialmente quando houver mais de um arquivo relacionado.

Melhores usos:

- completar stubs
- ajustar testes
- editar pequenos trechos interligados
- manter contexto Git durante a implementação

### mypy

Não tratar como bloqueador agora. Só respeitar tipos já existentes sem elevar escopo.

## 11. Regras objetivas para o DeepSeek

### Regra 1 — Não expandir escopo
Se não fecha a Fase 1, deve ser adiado.

### Regra 2 — Não refatorar por estética
Refatorar somente se bloquear a entrega.

### Regra 3 — Completar o que já existe
Preferir completar código parcial em vez de criar estrutura nova paralela.

### Regra 4 — Fazer happy path primeiro
Edge cases só depois do fluxo principal funcional.

### Regra 5 — Validar em ciclos curtos
Cada bloco relevante deve terminar com verificação local e teste.

### Regra 6 — Documentar o mínimo necessário
Documentação curta, prática e orientada à execução.

## 12. Entregáveis esperados ao final da Fase 1

Ao final desta fase, o DeepSeek deve entregar:

- fluxo inbound funcional
- criação e resolução de contato
- conversa criada ou recuperada corretamente
- mensagem inbound persistida
- roteiro ativo utilizado no fluxo
- resposta da IA gerada e registrada
- outbound funcional ou claramente simulável
- testes básicos automatizados
- documentação curta de execução

## 13. Prompt base para passar ao DeepSeek

```text
Continue o projeto considerando apenas a Fase 1 do Agente de Pesquisa. Não amplie escopo para handoff, painel completo, métricas, multi-instância ou multiagente. Seu objetivo é fechar a fatia vertical mínima funcional: inbound webhook -> idempotência -> contato -> conversa -> mensagem inbound -> roteiro ativo -> contexto mínimo -> chamada de LLM -> outbound -> persistência -> testes. Reaproveite ao máximo a arquitetura, routers, schemas, models e testes já existentes. Evite refatoração ampla. Trabalhe do jeito mais produtivo possível, em ciclos curtos, usando as ferramentas já instaladas no projeto: Ruff, pre-commit, pytest, GitHub Actions, Makefile e Aider. Sempre priorize completar stubs e wiring existente antes de criar novas abstrações.
```

## 14. Conclusão final

Se a meta é trabalhar da forma mais produtiva possível e gastar o menor tempo possível no desenvolvimento, a melhor decisão é:

- fechar apenas a **Fase 1** agora
- entregar um fluxo completo, ainda que simples
- deixar claramente anotado o que fica para fases posteriores

O maior risco neste momento não é técnico. É ampliar escopo cedo demais.
