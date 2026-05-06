# Fase 2 — Estrutura Operacional

**Objetivo:** preparar a base para operação com maior controle.
**Estimativa:** 60 a 90 horas

## 1. Entregas previstas
1. Cadastro de agentes
2. Configuração de instâncias/canais
3. Vínculo entre agentes e operação
4. Base para roteamento futuro

## 2. Escopo detalhado
### 2.1 Cadastro de agentes (research_agents)
- Tabela `research_agents` já existe (criada no Sprint 5+)
- Criar endpoints CRUD completos
- Criar testes unitários e E2E

### 2.2 Configuração de instâncias/canais
- Criar tabela `instances` para gerenciar múltiplas instâncias Evolution API
- Criar endpoints CRUD para instâncias
- Adaptar webhook service para suportar múltiplas instâncias

### 2.3 Vínculo entre agentes e operação
- Tabela associativa `agent_assignments`
- Criar endpoints de vinculação/desvinculação

### 2.4 Base para roteamento futuro
- Implementar lógica de seleção de agente disponível
- Criar fila interna de conversas aguardando atendimento
- Preparar estrutura para handoff humano (Fase 3)

## 3. O que NÃO fazer nesta fase
- Handoff humano completo (Fase 3)
- Painel operacional completo (Fase 3)
- Múltiplos canais avançados
- Dashboard analítico real (Fase 5)
- RBAC completo (Fase 5)

## 4. Estratégia de desenvolvimento
1. Criar branch: `feat/fase2-estrutura-operacional`
2. Completar CRUD de agentes primeiro
3. Criar tabela de instâncias e endpoints
4. Vincular agentes a instâncias
5. Implementar roteamento mínimo
6. Testar tudo com pytest + E2E
7. Documentar endpoints via Swagger

## 5. Ferramentas a usar
- just lint e just test para qualidade
- Aider para edições multi-arquivo
- pytest + GitHub Actions para CI/CD
- Cursor Pro para edição principal

## 6. Estimativa por etapa
| Etapa | Horas |
|-------|-------|
| CRUD de agentes | 10 a 15h |
| Tabela de instâncias/canais | 8 a 12h |
| Vínculo agente-instância | 6 a 10h |
| Roteamento mínimo | 10 a 15h |
| Testes | 12 a 18h |
| Documentação | 4 a 6h |
| Ajustes finais | 4 a 6h |
| **Total** | **54 a 82h** |

## 7. Checklist de pronto
- [ ] CRUD de agentes funcional
- [ ] CRUD de instâncias/canais funcional
- [ ] Agentes vinculados a instâncias
- [ ] Roteamento mínimo implementado
- [ ] Testes unitários + E2E passando
- [ ] Documentação dos endpoints no Swagger
- [ ] Branch mergeada na main
- [ ] Deploy no servidor Oracle

**Documento gerado em 05/05/2026 — Projeto Agente de Pesquisa**
