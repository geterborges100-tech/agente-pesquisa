# ADR-002: Postergação da Fase 2 — Estrutura Operacional

**Status:** Aceito
**Data:** 2026-05-06
**Decisão tomada por:** Geter Borges

## Contexto
A Fase 2 prevê cadastro de agentes, configuração de instâncias/canais, vínculo entre agentes e operação,
e base para roteamento futuro. O projeto atualmente opera com um único desenvolvedor, uma única instância
Evolution API (`instancia-pesquisa`) e não possui demanda imediata por múltiplos agentes ou canais.

## Decisão
Postergar a implementação da Fase 2 para um momento em que houver necessidade real de múltiplos agentes
ou múltiplas instâncias. O foco será direcionado para funcionalidades que tragam valor imediato ao usuário
final do agente (quem conversa com o WhatsApp).

## Alternativas consideradas
- **Manter a Fase 2 agora:** 60-90h de esforço para funcionalidades que não serão usadas no curto prazo.
- **Pular para Fase 3 (Handoff):** exige parcialmente a Fase 2, mas pode ser implementado de forma simplificada sem cadastro formal.
- **Focar em melhorias de experiência do agente:** roteiro de pesquisa, persona do Gemini, handoff simples.

## Consequências
### Positivas
- ~60-90h de desenvolvimento redirecionadas para funcionalidades de maior impacto imediato.
- Menor complexidade no código enquanto o uso é solo.
- Ciclos de feedback mais curtos com usuários reais.

### Riscos
- Se surgir demanda por múltiplos agentes/instâncias, a implementação será feita sob pressão.
- O handoff humano (Fase 3) precisará de adaptações para funcionar sem a estrutura completa da Fase 2.

## Próxima fase prioritária
**Fase 4 — Configuração Avançada e IA** (parcial):
- Criar um roteiro de pesquisa real (ResearchScript).
- Refinar o system prompt do Gemini para o tom adequado.
- Testar o guardrail PII com dados reais.

**Fase 3 — Handoff e Operação Assistida** (versão simplificada):
- Implementar handoff para um número fixo (sem fila operacional).
- Permitir envio manual de mensagens pelo painel existente.
