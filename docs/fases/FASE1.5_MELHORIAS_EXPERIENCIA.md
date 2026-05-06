# Guia DeepSeek — Fase 1.5 — Melhorias de Experiência do Agente

**Data:** 06/05/2026
**Status:** Em andamento
**Motivo:** Postergação da Fase 2 (ver ADR-002)

## Contexto
A Fase 2 (Estrutura Operacional) foi postergada porque o projeto opera com um único desenvolvedor,
uma única instância Evolution API, e não há demanda imediata por múltiplos agentes ou canais.
O foco será redirecionado para funcionalidades que melhorem a experiência do usuário final
(quem conversa com o agente no WhatsApp).

## Entregas previstas

| Prioridade | Tarefa | Horas estimadas |
|-----------|--------|-----------------|
| 1 | Criar um roteiro de pesquisa real (ResearchScript) | 3 a 5h |
| 2 | Refinar o system prompt do Gemini (persona do agente) | 2 a 3h |
| 3 | Handoff humano simplificado (número fixo) | 4 a 6h |
| 4 | Testar guardrail PII com dados reais | 1 a 2h |
| **Total** | | **10 a 16h** |

## Detalhamento das tarefas

### 1. Criar um roteiro de pesquisa (ResearchScript)
- Usar a tabela `research_scripts` já existente
- Criar um JSON com perguntas estruturadas (ex: nome, idade, opinião sobre produto)
- Carregar o script ativo no AIEngine (via `ScriptLoader`)
- Testar o fluxo completo: webhook → consentimento → perguntas do roteiro → respostas → finalização

### 2. Refinar o system prompt do Gemini
- Ajustar o `_SYSTEM_TEMPLATE` em `prompt_builder.py`
- Definir tom de voz, regras de comportamento, limites de conhecimento
- Testar diferentes versões e comparar qualidade das respostas

### 3. Handoff humano simplificado
- Quando o agente detectar que não sabe responder (ou o usuário pedir), enviar mensagem para um número fixo
- Não requer fila operacional, múltiplos agentes, nem painel completo
- Pode ser implementado como uma regra no `ai_engine.py`: se confiança < threshold → handoff

### 4. Testar guardrail PII
- Forçar o Gemini a gerar perguntas com CPF, telefone, etc.
- Verificar se o `GuardrailValidator` bloqueia antes do envio
- Registrar ocorrências no `audit_log`

## O que NÃO fazer nesta fase
- Cadastro de múltiplos agentes (Fase 2)
- Múltiplas instâncias/canais (Fase 2)
- Fila operacional completa (Fase 3)
- Painel de acompanhamento (Fase 3)
- Métricas e dashboard (Fase 5)

## Checklist de pronto
- [ ] Roteiro de pesquisa funcional (3+ perguntas)
- [ ] System prompt refinado e testado
- [ ] Handoff simples implementado
- [ ] Guardrail PII validado com dados reais
- [ ] Testes atualizados (pytest)
- [ ] Documentação atualizada
