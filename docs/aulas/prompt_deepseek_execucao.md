# PROMPT PARA O DEEPSEEK — Agente de Pesquisa
# Cole este prompt diretamente no DeepSeek para cada tarefa

---

## CONTEXTO DO PROJETO (cole sempre no início da conversa)

Você é um assistente técnico especializado em Python/FastAPI e Docker.
Estou desenvolvendo um projeto chamado **Agente de Pesquisa**.

**Stack do projeto:**
- Python / FastAPI
- PostgreSQL (banco principal do agente)
- Docker + Docker Compose
- Evolution API (webhooks WhatsApp/Instagram)
- OpenRouter / Gemini (LLM)
- Servidor de produção: Oracle Cloud Ubuntu 22.04 — 1 GB RAM
- Ambiente de dev: Windows 11 + WSL2 + Docker Desktop
- Repositório: github.com/geterborges100-tech/agente-pesquisa

**Estrutura atual do repositório:**
```
agente-pesquisa/
├── app/
│   ├── main.py
│   ├── routers/
│   └── services/
│       ├── ai_engine.py
│       ├── conversation_service.py
│       ├── evolution_webhook_service_fixed.py
│       ├── llm_client.py
│       ├── prompt_builder.py
│       └── script_loader.py
├── docs/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env (não versionado)
```

**Regras que você deve seguir:**
- Nunca use bibliotecas que não estejam no requirements.txt sem avisar
- Sempre gere código compatível com Python 3.11
- Sempre use variáveis de ambiente para credenciais (nunca hardcode)
- Prefira soluções simples e diretas — o servidor tem apenas 1 GB de RAM
- Quando gerar arquivos de configuração, inclua comentários explicativos
- Quando gerar commits, use o padrão Conventional Commits

---

## TAREFA 1 — Gerar o arquivo .env do TimeTracker

**O que preciso:**
Gere o arquivo `.env` para o TimeTracker (github.com/DRYTRIX/TimeTracker)
configurado para usar o PostgreSQL já existente no meu projeto.

**Parâmetros do meu PostgreSQL atual (do docker-compose.yml do agente):**
- Host interno Docker: `postgres` (nome do serviço)
- Porta: `5432`
- Banco do agente: `research_agent_db`
- Usuário: `research_user`
- Senha: `[SUBSTITUIR PELA SUA SENHA REAL]`

**O que quero:**
- O TimeTracker deve usar um banco separado: `timetracker_db`
- Mesmo usuário e senha do banco do agente (para simplificar)
- Porta da interface web do TimeTracker: `5050`
- Modo: desenvolvimento local (DEBUG=True)
- Idioma: português se disponível

**Salvar como:** `timetracker/.env`

---

## TAREFA 2 — Gerar o docker-compose.yml do TimeTracker

**O que preciso:**
Gere o arquivo `docker-compose.yml` para subir o TimeTracker
integrado à rede Docker do meu projeto principal.

**Requisitos:**
- O TimeTracker deve se conectar ao serviço `postgres` já existente na rede `agente_network`
- Não deve subir um PostgreSQL novo (já tenho um)
- Porta exposta: `5050:5000` (ou a porta padrão do TimeTracker)
- Deve usar as variáveis do arquivo `.env` gerado na Tarefa 1
- Deve ter `restart: unless-stopped`
- Deve ter healthcheck básico

**Rede Docker do meu projeto principal:**
```yaml
networks:
  agente_network:
    external: true
```

**Salvar como:** `timetracker/docker-compose.yml`

---

## TAREFA 3 — Gerar o arquivo .github/workflows/ci.yml

**O que preciso:**
Gere um workflow do GitHub Actions para CI do projeto.

**Requisitos:**
- Disparar em: push para qualquer branch e pull_request para main
- Jobs:
  1. **lint** — rodar `ruff check .` e `ruff format --check .`
  2. **test** — rodar `pytest tests/ -v` com cobertura mínima
- Python: 3.11
- Instalar dependências do `requirements.txt`
- Usar cache de pip para acelerar
- Não fazer deploy automático (apenas validação)

**Salvar como:** `.github/workflows/ci.yml`

---

## TAREFA 4 — Gerar o arquivo .pre-commit-config.yaml

**O que preciso:**
Gere o arquivo de configuração do pre-commit para o projeto.

**Requisitos:**
- Usar `ruff` para lint e formatação
- Verificar arquivos grandes (>500KB)
- Verificar trailing whitespace
- Verificar fim de arquivo
- Verificar conflitos de merge não resolvidos
- Não bloquear commits por falha de testes (apenas lint)

**Salvar como:** `.pre-commit-config.yaml`

---

## TAREFA 5 — Gerar o script de deploy para Oracle Cloud

**O que preciso:**
Gere um script bash `deploy.sh` para fazer deploy automático
no servidor Oracle Cloud via SSH.

**Parâmetros:**
- Usuário SSH: `ubuntu`
- IP do servidor: `[SUBSTITUIR PELO SEU IP]`
- Chave SSH: `~/.ssh/oracle_key.pem`
- Diretório do projeto no servidor: `/home/ubuntu/agente-pesquisa`
- Branch de produção: `main`

**O que o script deve fazer:**
1. Conectar via SSH
2. Fazer `git pull origin main`
3. Rodar `docker compose up -d --force-recreate`
4. Aguardar 10 segundos
5. Checar se o container `research_agent_api` está rodando
6. Exibir os últimos 20 logs do container
7. Exibir mensagem de sucesso ou falha

**Requisitos:**
- Usar `set -e` para parar em caso de erro
- Colorir output (verde = sucesso, vermelho = erro)
- Não expor senhas no script

**Salvar como:** `scripts/deploy.sh`

---

## TAREFA 6 — Gerar mock do webhook da Evolution API

**O que preciso:**
Gere um arquivo Python com um mock do webhook da Evolution API
para usar nos testes locais sem precisar do ngrok.

**Requisitos:**
- Simular o payload JSON que a Evolution API envia para o agente
- Cobrir os casos:
  1. Mensagem de texto simples recebida
  2. Mensagem de áudio recebida
  3. Mensagem de imagem recebida
  4. Evento de conexão/status
- Usar `pytest` e `httpx` para fazer requisições ao FastAPI local
- Incluir fixture reutilizável com o payload base
- Incluir comentários explicando cada campo do payload

**Salvar como:** `tests/mocks/evolution_webhook_mock.py`

---

## TAREFA 7 — Gerar documento de decisão do TimeTracker

**O que preciso:**
Gere um arquivo Markdown documentando a decisão de usar o TimeTracker.

**Conteúdo:**
- Data da decisão: 01/05/2026
- Problema que resolve: controle de horas previstas vs realizadas por tarefa
- Alternativas consideradas: Kimai, OpenProject, Clockify, módulo próprio
- Motivo da escolha: forecast/burn rate mais forte, open source, PostgreSQL, Docker
- Como usar no dia a dia: estimativa antes, registro após, revisão semanal
- Link do repositório: github.com/DRYTRIX/TimeTracker

**Salvar como:** `docs/decisoes/timetracker.md`

---

## COMO USAR ESTE PROMPT

1. Abra o DeepSeek (chat.deepseek.com)
2. Cole o bloco **CONTEXTO DO PROJETO** no início
3. Cole apenas a **TAREFA** que você quer executar agora
4. Peça ao DeepSeek para gerar o arquivo
5. Copie o resultado e aplique com o Cursor ou diretamente no terminal
6. Faça o commit conforme orientado no roteiro

**Dica:** Não cole todas as tarefas de uma vez.
Cole uma tarefa por vez para ter respostas mais precisas.

---

## COMMITS APÓS CADA TAREFA

| Tarefa | Comando de commit |
|--------|-------------------|
| 1 e 2  | `git commit -m "chore: add TimeTracker docker setup with PostgreSQL integration"` |
| 3      | `git commit -m "ci: add GitHub Actions lint and test workflow"` |
| 4      | `git commit -m "chore: add pre-commit config with ruff"` |
| 5      | `git commit -m "ci: add automated deploy script for Oracle Cloud"` |
| 6      | `git commit -m "test: add Evolution API webhook mock for local testing"` |
| 7      | `git commit -m "docs: add TimeTracker decision record"` |