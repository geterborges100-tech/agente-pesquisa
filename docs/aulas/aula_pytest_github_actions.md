# Aula: pytest + GitHub Actions — Testes Automatizados e CI/CD

## O que é o pytest?
- **Framework de testes automatizados** para Python, o mais popular e simples de usar.
- Permite escrever funções de teste que verificam se o código se comporta como esperado.
- Seu projeto já possui testes em `tests/`, cobrindo partes críticas como:
  - `ConversationService` (criar conversas, extrair texto de mensagens)
  - `WebhookService` (validação de assinatura, idempotência)
- Com um único comando, você descobre o que quebrou desde a última alteração.

## O que são GitHub Actions?
- **Serviço de CI/CD** nativo do GitHub.
- Cria **workflows** que disparam automaticamente em eventos do Git (push, pull request).
- Esses workflows rodam em máquinas virtuais e podem executar qualquer script.
- No nosso projeto, eles serão usados para:
  - Rodar o **pytest** a cada push/PR.
  - Rodar o **Ruff** para garantir que o estilo continua correto.
- Resultado: ✅ verde se tudo passou, ❌ vermelho se algo falhou (e você recebe notificação).

## Como eles se complementam?

| Ferramenta | O que verifica? | Quando age? |
|-----------|-----------------|-------------|
| **Ruff** | Estilo, sintaxe, imports, formatação | Antes do commit (pre‑commit) |
| **pytest** | Lógica de negócio, comportamento esperado | Durante o push/PR (CI) |
| **GitHub Actions** | Executa pytest + Ruff automaticamente | No servidor do GitHub |

- Ruff + pre‑commit → barra erros **locais** antes do commit.
- pytest + GitHub Actions → barra erros de **lógica** no repositório remoto, mesmo que você esqueça de rodar os testes manualmente.

## Na prática
1. Rodar os testes localmente: `python -m pytest tests/ -v`
2. Corrigir eventuais falhas.
3. Criar o workflow do GitHub Actions (`.github/workflows/test.yml`).
4. Commitar e dar push — os testes serão executados automaticamente a partir daí.

**Benefício:** você nunca mais precisa lembrar de rodar os testes manualmente; o GitHub fará isso e te avisará se algo quebrou.
