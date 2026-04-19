# Deploy Guide — Instagram Research Agent
## Oracle Cloud · Ubuntu 22.04 · 1 GB RAM

---

### 1. Pré-requisitos no servidor

```bash
# Docker + Docker Compose plugin (uma vez só)
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker
```

---

### 2. Subir pela primeira vez

```bash
# Clone / copie os arquivos para o servidor, entre na pasta raiz e:

# Preencha as senhas antes de tudo
nano .env

# Build + subida em background
docker compose up -d --build

# Acompanhe os logs na subida
docker compose logs -f
```

---

### 3. Verificar saúde dos containers

```bash
# Status geral
docker compose ps

# Health check da API
curl http://localhost:8000/health
# Esperado: {"status":"healthy"}

# Consumo de memória em tempo real
docker stats --no-stream
# Referência esperada:
#   research_agent_db   ~80–120 MB
#   research_agent_api  ~80–140 MB
#   Total               ~160–260 MB  ← seguro para 1 GB
```

---

### 4. Comandos do dia a dia

```bash
# Parar tudo (preserva dados)
docker compose down

# Reiniciar só a API (após deploy de novo código)
docker compose up -d --build api

# Ver logs da API (últimas 100 linhas + follow)
docker compose logs -f --tail=100 api

# Acessar o Postgres diretamente
docker exec -it research_agent_db psql -U agent -d research_agent
```

---

### 5. Executar migrations / DDL inicial

```bash
# Rodar o DDL pela primeira vez (cria todas as tabelas)
docker exec -i research_agent_db psql -U agent -d research_agent < ddl_v1.sql

# OU deixar o create_all_tables() do lifespan criar automaticamente
# (já está configurado em database.py — ocorre na primeira subida)
```

---

### 6. Limites de memória — referência

| Container | Limit | Reserva | Nota |
|---|---|---|---|
| `research_agent_db` | 384 MB | 128 MB | Postgres 15 tunado para baixa RAM |
| `research_agent_api` | 256 MB | 64 MB | 1 worker Uvicorn |
| **SO + Docker daemon** | ~200 MB | — | Ubuntu 22.04 mínimo |
| **Total estimado** | **~840 MB** | — | Margem de ~180 MB |

> Se o OOM Killer agir, `restart: always` vai recuperar automaticamente.
> Monitore com `free -h` no host e `docker stats` nos containers.

---

### 7. Próximos passos (Sprint 2)

Após validar o deploy do Sprint 1:
1. Registrar o webhook no painel Meta for Developers
2. Testar o handshake de verificação (`GET /webhooks/meta/instagram`)
3. Enviar uma mensagem de teste e validar os logs
4. Abrir nova conversa para o Sprint 2 — Motor de IA
