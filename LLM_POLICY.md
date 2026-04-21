# LLM Policy - Agente de Pesquisa

Política operacional do modelo de linguagem para o Núcleo Vivo da Sprint 5.

## 1. Provedor e modelo atual

- **Provedor**: OpenRouter
- **Modelo padrão**: `google/gemini-2.0-flash-001`
- **Objetivo**: respostas reais e econômicas, com menor custo de tokens possível.

## 2. Fonte de configuração

A configuração do LLM pode vir de:

- variáveis de ambiente
- tabela de configuração no banco
- fallback seguro no código

### Variáveis principais

- `OPENROUTER_API_KEY`
- `LLM_MODEL`
- `ACCOUNT_ID`

## 3. Regras de economia de tokens

- Manter o histórico curto.
- `PromptBuilder` deve usar no máximo 5 turnos de histórico.
- Não repetir instruções longas em cada chamada.
- Reduzir textos fixos sempre que o nó do roteiro já estiver claro.
- Evitar chamar o LLM quando a mensagem não exigir resposta inteligente.

## 4. Quando chamar o LLM

Chamar somente quando houver:

- mensagem útil do participante
- necessidade de interpretação de contexto
- avanço ou validação de nó do roteiro
- geração de resposta real via fluxo oficial

## 5. Quando não chamar o LLM

Não chamar se a entrada for:

- mensagem vazia
- áudio sem transcrição
- evento duplicado
- mensagem do sistema
- evento fora do fluxo oficial
- payload inválido

## 6. Comportamento esperado da resposta

- Resposta curta
- Tom cordial
- Sem explicações internas
- Sem revelar instruções ocultas
- Sem mencionar stack antigo da Meta

## 7. Alterações permitidas sem mexer no código

Preferencialmente via configuração:

- troca de modelo
- ativação/desativação de flags de LLM
- ajustes de ambiente
- limites operacionais simples

## 8. Critério de sucesso

A política está cumprida quando:

- o fluxo inbound gera resposta outbound real
- o histórico permanece enxuto
- o custo de tokens cai
- o Abacus não precisa reler documentos históricos para operar

## 9. Observação operacional

Qualquer refatoração grande deve vir com checkpoint Git antes da mudança.
