# Método Oficial de Desenvolvimento com Abacus

## Objetivo
Maximizar produtividade, reduzir retrabalho e economizar créditos do Abacus.AI no desenvolvimento do projeto **Agente de Pesquisa Instagram/WhatsApp**.

## Premissas
- Gemini rápido é a ferramenta padrão para tarefas baratas e frequentes.
- ChatLLM é usado para coordenação, revisão, síntese e debugging orientado.
- Abacus AI Agent deve ser usado de forma cirúrgica, quando o ganho de produtividade justificar o custo.
- O foco é avançar o produto com micro-entregas estáveis.
- O projeto está em fase de evolução controlada, não em refatoração ampla.
- Claude não entra como ferramenta principal nesta versão do método.

## Resumo Executivo
A estratégia oficial é:
- usar **Gemini rápido** como copiloto principal do dia a dia;
- usar **ChatLLM** para planejar, revisar, debugar e consolidar decisões;
- usar **Abacus AI Agent** apenas quando houver tarefa estrutural, bloqueio real ou mudança multiarquivo de maior risco.

O desenvolvimento deve ocorrer em **micro-sprints econômicos**, com checkpoints frequentes e validações curtas.

## Decisão de Uso por Ferramenta

### Gemini rápido
Usar para:
- quebrar tarefas;
- revisar logs;
- sugerir patches pequenos;
- desenhar testes mínimos;
- gerar documentação curta;
- analisar tracebacks e erros localizados.

### ChatLLM
Usar para:
- consolidar plano técnico;
- revisar critério de aceite;
- organizar sprint;
- fazer revisão de arquitetura leve;
- sintetizar status, decisões e próximos passos.

### Abacus AI Agent
Usar para:
- mudanças difíceis em múltiplos arquivos;
- revisão de fluxo crítico;
- investigação de bugs difíceis;
- plano de refatoração controlada;
- geração de artefatos maiores quando o ganho operacional for claro.

Evitar usar para:
- dúvidas simples;
- tarefas mecânicas;
- logs curtos;
- patch localizado em 1 arquivo;
- perguntas que podem ser resolvidas com contexto mínimo.

## Recomendação de Plano Abacus

### Pro
Recomendado se o orçamento permitir, porque aumenta margem operacional e reduz gargalo de uso do AI Agent.

### Basic
Viável com disciplina forte, desde que o uso do AI Agent seja raro e o fluxo principal fique concentrado em Gemini rápido + ChatLLM.

## Modelo Operacional Oficial

### Passo 1 — Definir uma micro-entrega fechada
A entrega precisa ser pequena, objetiva e testável.

Exemplos:
- aplicar consent gate;
- corrigir migration;
- validar cenário E2E específico.

### Passo 2 — Desenhar a solução mais barata
Antes de codar, pedir uma solução mínima.

Perguntas obrigatórias:
- qual é o menor patch possível?
- quais arquivos serão afetados?
- qual é o principal risco?
- qual é a validação mínima?

### Passo 3 — Implementar pequeno
Regras:
- preferir mudanças em 1 a 3 arquivos;
- não misturar refatoração com feature;
- não reabrir partes estáveis sem necessidade;
- trabalhar com checkpoint mental claro.

### Passo 4 — Fazer validação curta e obrigatória
Validar sempre:
- imports;
- subida de container;
- smoke test;
- cenário principal;
- cenário de falha previsível.

### Passo 5 — Criar checkpoint
Registrar:
- o que mudou;
- o que foi validado;
- o que ficou pendente;
- commit/tag/checkpoint relevante.

### Passo 6 — Abrir nova conversa quando fizer sentido
Abrir nova conversa quando:
- a micro-entrega estiver encerrada;
- o contexto do chat estiver poluído;
- o assunto técnico mudar de natureza;
- o raciocínio começar a ficar repetitivo.

## Matriz Ideal de Uso

### Use Gemini rápido quando:
- a tarefa for operacional;
- o escopo for pequeno;
- o custo precisar ser mínimo;
- você quiser velocidade com baixa sofisticação.

### Use ChatLLM quando:
- precisar organizar raciocínio;
- revisar plano;
- refinar critério de aceite;
- fechar um checkpoint.

### Use Abacus AI Agent quando:
- o problema durar mais de 20 a 30 minutos sem avanço real;
- houver impacto em 4 ou mais arquivos relevantes;
- existir risco estrutural entre camadas;
- você precisar de uma investigação mais profunda com maior produtividade.

## Regra de Escalonamento
Escalar para **Abacus AI Agent** se:
- a tarefa não evoluir após 20 a 30 minutos de boa tentativa com Gemini rápido e validação local;
- envolver múltiplos componentes;
- exigir visão ampla de arquitetura;
- houver repetição de erro ou retrabalho.

## Distribuição Recomendada de Uso
- **70% a 85%**: Gemini rápido
- **10% a 20%**: ChatLLM
- **5% a 15%**: Abacus AI Agent

## Política de Economia de Créditos
Princípios:
- não usar ferramenta cara para pensamento básico;
- evitar pedidos grandes demais;
- sempre fornecer contexto mínimo de alta qualidade;
- reutilizar briefing do projeto;
- fechar um tema antes de abrir outro;
- evitar gerar artefatos pesados sem necessidade;
- revisar consumo semanalmente.

## Estimativa de Créditos
Como os créditos variam pelo uso e não há tabela fixa pública por tipo de operação, a melhor prática é trabalhar com faixas.

### Cenário super econômico
- uso muito disciplinado do AI Agent;
- foco em Gemini rápido.

Estimativa:
- **baixo consumo mensal**

### Cenário equilibrado
- alguns escalonamentos pontuais;
- uso do ChatLLM para revisão;
- AI Agent só em tarefas críticas.

Estimativa:
- **faixa saudável recomendada para este projeto**

### Cenário intensivo
- uso frequente do AI Agent;
- prompts grandes;
- investigação profunda recorrente.

Estimativa:
- **consumo alto, a evitar sem necessidade**

## Cadência Semanal Recomendada

### Segunda-feira
- revisar status do sprint;
- escolher micro-entregas;
- ordenar por risco e dependência.

### Terça a quinta
- executar 1 a 2 micro-entregas por dia;
- validar e registrar checkpoint.

### Sexta-feira
- revisar o que foi entregue;
- revisar consumo de créditos;
- preparar foco da semana seguinte.

## Regras de Produtividade
- fazer pedidos curtos e focados;
- separar design, implementação, revisão e validação;
- sempre informar erro exato quando houver;
- definir critério de aceite antes do patch;
- abrir nova conversa quando o chat perder foco.

## Método Oficial para Sprint 5 em Diante
1. escolher uma micro-entrega;
2. desenhar a solução mais barata;
3. implementar pequeno;
4. validar curto;
5. registrar checkpoint;
6. só então avançar para a próxima fatia.

## Prompts-Padrão

### Planejamento barato
> Qual o menor patch possível para esta tarefa? Liste arquivos afetados, risco principal e validação mínima.

### Debug econômico
> Analise este erro com base neste trecho, neste comportamento esperado e no último ponto estável. Diga a causa mais provável e o menor teste para validar.

### Escalonamento
> Esta tarefa ficou bloqueada após tentativa objetiva. Resuma o problema, os arquivos afetados, as hipóteses já descartadas e proponha o próximo passo com menor risco.

### Revisão econômica
> Revise esta solução apenas quanto a risco, regressão e consistência com o critério de aceite.

## Indicadores de Sucesso
- menos retrabalho;
- mais micro-entregas fechadas por semana;
- menor uso desnecessário do AI Agent;
- mais previsibilidade de avanço;
- checkpoints mais claros.

## Sinais de Alerta
- chat muito longo e confuso;
- mudança grande demais sem critério de aceite;
- uso cedo demais do AI Agent;
- retrabalho repetido em pontos já estáveis;
- debug sem teste mínimo.

## Conclusão
O método oficial recomendado para este projeto é:
- **Gemini rápido como padrão**;
- **ChatLLM como coordenador e revisor**;
- **Abacus AI Agent como ferramenta de escalonamento inteligente**.

O objetivo não é usar a ferramenta mais poderosa o tempo todo, mas usar a ferramenta certa no momento certo para entregar mais, com menos custo e menos retrabalho.
