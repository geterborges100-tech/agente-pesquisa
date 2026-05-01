#!/bin/bash
set -e

# Configura??es
SERVER_IP="136.248.65.156"
SSH_USER="ubuntu"
SSH_KEY="$HOME/.ssh/agente_pesquisa_key"
PROJECT_DIR="/home/ubuntu/agente-pesquisa"
BRANCH="main"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "?? Iniciando deploy em $SERVER_IP..."

ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << EOF
    set -e
    cd $PROJECT_DIR
    echo "?? Atualizando c?digo da branch $BRANCH..."
    git pull origin $BRANCH
    echo "?? Recriando containers..."
    docker compose up -d --force-recreate
    sleep 10
    echo "?? Verificando container..."
    if docker ps --filter "name=research_agent_api" --filter "status=running" | grep -q research_agent_api; then
        echo -e "${GREEN}? Deploy conclu?do com sucesso!${NC}"
        echo "?? ?ltimos logs:"
        docker compose logs api --tail=20
    else
        echo -e "${RED}? Container research_agent_api n?o est? rodando!${NC}"
        docker compose logs api --tail=30
        exit 1
    fi
EOF
