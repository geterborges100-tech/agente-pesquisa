# Aula: Ruff + pre-commit na Rotina de Desenvolvimento

## O que é o Ruff?
- **Linter**: analisa o código e aponta erros (sintaxe, imports não usados, más práticas).
- **Formatador**: padroniza estilo (aspas, espaçamento, tamanho de linha) — similar ao Black, mas muito mais rápido.
- **Corretor**: com `--fix`, ele mesmo resolve problemas simples (imports duplicados, variáveis não usadas).

## O que é o pre-commit?
- É um **gancho** (hook) do Git: uma barreira automática que executa scripts **antes de cada commit**.
- Se qualquer script falhar, o commit é **bloqueado** até você corrigir o erro.
- Isso garante que código sujo/errado nunca entre no repositório.

## Como eles trabalham juntos (fluxo real)
1. Você altera código.
2. `git add .`
3. `git commit`
4. O pre-commit ativa o Ruff:
   - Ruff analisa e corrige o que for possível.
   - Se houver erros → commit **bloqueado**.
   - Se tudo passar → Ruff formata o código.
   - Se a formatação falhar → commit **bloqueado**.
5. Commit **concluído** apenas se todos os hooks passarem.

## Comandos essenciais
- Rodar Ruff manualmente:  
  `python -m ruff check app/ --fix`  
  `python -m ruff format app/`
- Rodar todos os hooks sem commit:  
  `python -m pre_commit run --all-files`
- Forçar commit ignorando hooks (emergência):  
  `git commit -m "mensagem" --no-verify`

## Gotchas (coisas que podem te pegar)
- **LF/CRLF**: O Ruff converte automaticamente conforme seu SO.
- **Arquivos excluídos**: `_referencia/`, `__pycache__` etc. são ignorados.
- **Imports duplicados**: removidos automaticamente.

## Economia de tempo
Antes: código quebrado só era descoberto quando o container falhava.  
Agora: o pre-commit barra erros em segundos, antes mesmo do commit.
