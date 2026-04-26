# Checklist Operacional Diário com Estimativa de Horas

## Projeto
**Agente de Pesquisa Instagram/WhatsApp**

## Contexto
Sprint 5 em diante.
Base da estratégia:
- Gemini rápido como ferramenta principal;
- ChatLLM para coordenação e revisão;
- Abacus AI Agent apenas para uso cirúrgico.

## Objetivo deste documento
Transformar o método oficial em um checklist diário simples de seguir, com estimativa de horas por tarefa, para maximizar produtividade e economizar créditos.

## Visão geral da rotina
Cada micro-entrega deve passar por:
1. definição;
2. desenho barato;
3. implementação pequena;
4. validação curta;
5. checkpoint;
6. decisão sobre continuar ou abrir nova conversa.

## Regras-mãe
- não trabalhar o sprint inteiro de uma vez;
- não misturar feature, refatoração e documentação no mesmo bloco;
- não usar Abacus AI Agent para problema simples;
- usar Gemini rápido como padrão no dia a dia;
- fechar uma micro-entrega antes de abrir outra;
- sempre ter critério de aceite antes de alterar código.

## Modelo de dia ideal
Carga diária recomendada de foco real:
- **4 a 6 horas líquidas**

Distribuição ideal:
- **20%** planejamento e revisão;
- **50%** implementação e testes;
- **20%** validação e debugging;
- **10%** documentação e checkpoint.

## Estrutura diária recomendada

### Bloco 1 — Abertura do dia
**Objetivo:** retomar contexto sem desperdiçar tempo nem créditos.

Tarefas:
1. revisar o último ponto estável — **10 a 15 min**
2. revisar o objetivo da micro-entrega do dia — **5 a 10 min**
3. confirmar critério de aceite — **5 a 10 min**
4. listar arquivos prováveis de impacto — **5 a 10 min**

**Tempo total:** 25 a 45 min

**Ferramenta recomendada:** Gemini rápido ou ChatLLM com contexto curto.

**Prompt sugerido:**
> Retome esta micro-entrega. Resuma objetivo, arquivos afetados, risco principal e critério de aceite em formato curto.

### Bloco 2 — Desenho barato da solução
**Objetivo:** descobrir o menor patch possível antes de codar.

Tarefas:
1. pedir decomposição da mudança — **10 a 15 min**
2. pedir risco de regressão — **5 a 10 min**
3. definir menor teste para validar — **5 a 10 min**
4. decidir se cabe em patch pequeno ou precisa escalonamento — **5 a 10 min**

**Tempo total:** 25 a 45 min

**Ferramenta recomendada:** Gemini rápido.

**Prompt sugerido:**
> Qual o menor patch possível para esta tarefa? Liste arquivos afetados, risco principal e validação mínima.

### Bloco 3 — Implementação da micro-entrega
**Objetivo:** executar a mudança com escopo pequeno e controlado.

Tarefas:
1. editar arquivo principal — **20 a 60 min**
2. ajustar arquivo secundário, se necessário — **15 a 45 min por arquivo**
3. revisar imports, contratos e chamadas afetadas — **10 a 20 min**
4. preparar teste manual ou automatizado mínimo — **15 a 40 min**

**Tempo total típico:** 1h a 2h30

**Ferramenta recomendada:**
- Gemini rápido para apoio pontual;
- ChatLLM para consolidar raciocínio;
- Abacus AI Agent apenas se a tarefa fugir do patch pequeno.

**Critérios para escalonar:**
- mudança tocando 4 ou mais arquivos relevantes;
- comportamento inconsistente em vários pontos do fluxo;
- debug repetitivo por mais de 20 a 30 minutos;
- necessidade de visão estrutural mais ampla.

### Bloco 4 — Validação curta obrigatória
**Objetivo:** provar rapidamente que a micro-entrega funciona e não quebrou o núcleo estável.

Tarefas:
1. validar imports — **5 min**
2. subir ou reiniciar container — **5 a 10 min**
3. executar smoke test — **10 a 20 min**
4. executar cenário principal — **10 a 20 min**
5. executar cenário de falha previsível — **10 a 20 min**
6. revisar logs essenciais — **10 a 15 min**

**Tempo total:** 50 min a 1h30

**Prompt sugerido:**
> Analise este erro com base neste trecho, neste comportamento esperado e no último ponto estável. Diga a causa mais provável e o menor teste para validar.

### Bloco 5 — Checkpoint e fechamento da fatia
**Objetivo:** encerrar a entrega com rastreabilidade e preparar o próximo passo.

Tarefas:
1. registrar o que mudou — **10 a 15 min**
2. registrar o que ainda falta — **5 a 10 min**
3. preparar mensagem de commit — **5 min**
4. criar checkpoint ou tag, se aplicável — **5 a 10 min**
5. decidir se é bom momento para abrir nova conversa — **5 min**

**Tempo total:** 30 a 45 min

## Sinais de que é um bom momento para iniciar nova conversa
- a micro-entrega acabou;
- existe um novo tema técnico diferente;
- o chat acumulou muitos logs e contexto irrelevante;
- o raciocínio começou a ficar repetitivo;
- a próxima tarefa é diferente em natureza.

## Checklist diário rápido

### Antes de codar
- definir a micro-entrega;
- escrever critério de aceite;
- listar arquivos principais;
- identificar risco principal;
- pedir o menor patch possível.

### Durante a implementação
- manter escopo pequeno;
- evitar refatoração paralela;
- validar a cada mudança relevante;
- não escalar cedo demais para o Abacus AI Agent.

### Antes de fechar o dia
- verificar se a micro-entrega ficou pronta;
- registrar status;
- anotar a próxima pendência;
- decidir se amanhã começa continuação ou nova fatia.

## Estimativa de horas por tipo de tarefa

### 1. Definição de micro-entrega
- **0,25h a 0,5h**

### 2. Desenho barato da solução
- **0,25h a 0,75h**

### 3. Implementação pequena em 1 arquivo
- **0,5h a 1,5h**

### 4. Implementação pequena em 2 a 3 arquivos
- **1,5h a 3h**

### 5. Debug localizado
- **0,5h a 1,5h**

### 6. Debug com impacto cruzado
- **1,5h a 3h**

### 7. Migration Alembic simples
- **0,75h a 1,5h**

### 8. Migration com validação de fluxo
- **1,5h a 3h**

### 9. Teste unitário pequeno
- **0,5h a 1,5h**

### 10. Teste E2E simples
- **1h a 2h**

### 11. Teste E2E mais completo
- **2h a 4h**

### 12. Revisão de logs e observabilidade
- **0,5h a 1h**

### 13. Documentação curta de checkpoint
- **0,25h a 0,5h**

### 14. Preparação de nova conversa limpa
- **0,15h a 0,3h**

### 15. Escalonamento para Abacus AI Agent
- **0,25h a 0,5h**

## Quando usar o Abacus AI Agent neste checklist
Usar somente se:
- o tempo gasto com tentativa local já passou de 20 a 30 minutos sem progresso real;
- a mudança afeta múltiplos pontos do sistema;
- há risco de regressão estrutural;
- o ganho potencial de produtividade é maior que o custo em créditos.

**Tempo típico de preparação para usar bem o AI Agent:** 15 a 30 min

## Rotina semanal recomendada

### Segunda-feira
1. revisar status do sprint — **20 a 30 min**
2. escolher 2 a 4 micro-entregas da semana — **30 a 45 min**
3. definir ordem e risco — **15 a 20 min**

**Tempo total:** 1h a 1h30

### Terça a quinta
1. executar 1 a 2 micro-entregas por dia — **2h30 a 5h por micro-entrega**
2. validar e fazer checkpoint — **30 a 45 min por dia**

**Tempo total por dia:** 3h a 6h

### Sexta-feira
1. revisar o que foi entregue — **20 a 30 min**
2. revisar consumo de créditos do Abacus — **10 a 15 min**
3. organizar pendências e próximo foco — **20 a 30 min**
4. preparar conversa nova para a próxima semana, se necessário — **10 a 20 min**

**Tempo total:** 1h a 1h30

## Estimativa de capacidade

### Semanal
- **3 a 6 micro-entregas pequenas**, ou
- **2 a 3 micro-entregas moderadas**

### Mensal
- **12 a 20 micro-entregas pequenas**, ou
- **8 a 12 micro-entregas moderadas**

## Como economizar créditos no dia a dia
- use Gemini rápido para planejamento, triagem, logs e patch pequeno;
- envie apenas trechos relevantes;
- não peça solução gigante;
- sempre leve o último ponto estável;
- encerre um assunto antes de abrir outro;
- abra conversa nova quando o contexto ficar poluído;
- use o AI Agent apenas para multiplicar produtividade em tarefas maiores.

## Template operacional de cada tarefa
- **Nome da tarefa:**
- **Objetivo:**
- **Escopo:**
- **Arquivos principais:**
- **Critério de aceite:**
- **Risco principal:**
- **Tempo estimado:**
- **Tempo real gasto:**
- **Resultado:**
- **Próximo passo:**

## Exemplo preenchido

**Nome da tarefa:** Sprint 5.1 — Aplicar consent gate no webhook

**Objetivo:** Bloquear o fluxo principal quando não houver consentimento válido.

**Escopo:** Alterar o webhook e validar a regra com cenários mínimos.

**Arquivos principais:**
- `evolution_webhook_service_fixed.py`
- `consent_repository.py`
- `guardrail_validator.py`

**Critério de aceite:** Sem consentimento válido, o fluxo não chama LLM nem outbound livre.

**Risco principal:** Bloquear usuários válidos por erro de checagem.

**Tempo estimado:**
- definição e desenho: **0,5h**
- implementação: **1h a 2h**
- validação: **1h**
- checkpoint: **0,25h**

**Tempo total estimado:** **2,75h a 3,75h**

## Conclusão
A melhor rotina é:
- escolher uma micro-entrega por vez;
- desenhar barato com Gemini rápido;
- implementar pequeno;
- validar curto;
- registrar checkpoint;
- iniciar nova conversa quando o contexto estiver naturalmente encerrado.
