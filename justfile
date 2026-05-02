# justfile para o projeto Agente de Pesquisa
# Execute: just <comando>

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Roda lint e formatação
lint:
    python -m ruff check app/ --fix
    python -m ruff format app/

# Roda todos os testes
test:
    python -m pytest tests/ -v

# Verifica lint antes do commit (igual ao pre-commit)
check:
    python -m pre_commit run --all-files

# Deploy rápido no servidor Oracle
deploy:
    ssh -i ssh-key-2026-03-09.key ubuntu@136.248.65.156 "cd ~/agente-pesquisa && git pull origin main && docker compose up -d --force-recreate && sleep 10 && docker logs research_agent_api --tail=10"

# Inicia o ambiente local (agente + banco)
up:
    docker compose up -d

# Para o ambiente local
down:
    docker compose down

# Reinicia a API local
restart:
    docker compose restart api
    sleep 5
    docker compose logs api --tail=10

# Abre o TimeTracker
timetracker:
    start http://localhost:5050

# Ajuda
help:
    just --list
