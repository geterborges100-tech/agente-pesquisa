# ADR-001: Ferramentas de Automação do Fluxo de Desenvolvimento

**Status:** Aceito
**Data:** 2026-05-01
**Decisão tomada por:** Geter Borges

## Contexto

O ciclo manual de desenvolvimento (IA gera código → copiar para o notebook → testar → reportar erro → IA corrigir) é lento, propenso a erros e não escalável. Precisamos de um fluxo automatizado que:

- Detecte erros de sintaxe e estilo automaticamente
- Execute testes a cada mudança de código
- Permita que a IA edite o código diretamente no repositório
- Unifique comandos repetitivos em um único ponto de entrada
- Garanta qualidade consistente antes de cada commit e push

## Decisão

Adotaremos cinco ferramentas open source, implementadas progressivamente:

| Ferramenta | Propósito | Justificativa |
|-----------|-----------|---------------|
| **Ruff + pre-commit** | Lint e formatação automática antes do commit | Detecta erros bobos (ex: imports duplicados, `async async def`, `from __future__` fora do lugar) em milissegundos |
| **pytest + GitHub Actions** | Testes automatizados a cada push/PR | O projeto já possui testes unitários; expandir e rodar automaticamente evita regressões silenciosas |
| **Makefile** | Comando único para lint + testes (`make check`) | Reduz a carga cognitiva de lembrar comandos separados |
| **Aider** | IA edita código diretamente com contexto Git | Elimina o ciclo manual de copiar/colar entre chat e editor |
| **mypy** | Checagem de tipos estáticos (futuro) | Será adotado quando o código tiver cobertura de tipos mais madura |

## Consequências

### Positivas
- **Menos retrabalho:** erros são pegos antes do commit, não depois de testar no WhatsApp.
- **Feedback rápido:** a IA recebe resultados de testes automaticamente, acelerando correções.
- **Padronização:** código consistente em estilo e qualidade.
- **Rastreabilidade:** GitHub Actions documenta o histórico de testes.

### Riscos
- **Curva de aprendizado:** Aider exige configuração inicial (OpenRouter + chaves).
- **Mypy prematuro:** adiado para evitar falsos positivos que atrapalhem o desenvolvimento.

## Referências

- [Documento de Automação do Fluxo de Desenvolvimento](docs/processo/automacao_desenvolvimento.md)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pre-commit Documentation](https://pre-commit.com)
- [Aider Documentation](https://aider.chat)
