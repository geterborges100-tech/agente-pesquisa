# 🚀 Automação do Desenvolvimento — Ferramentas e Fluxo de Trabalho

**Data:** 02/05/2026  
**Objetivo:** Documentar todas as ferramentas de automação instaladas no projeto.

## 📋 Ferramentas Instaladas
- **Ruff + pre-commit** – Lint e formatação automática antes do commit
- **pytest** – Testes unitários (python -m pytest tests/ -v)
- **GitHub Actions** – CI/CD (lint + testes a cada push/PR)
- **Aider** – Edição de código via terminal com IA
- **Cursor Pro** – IDE com IA integrada
- **TimeTracker** – Controle de horas e estimativas
- **Script de deploy** – Deploy rápido no servidor Oracle
- **Mock do webhook** – Testes locais sem ngrok
- **lint-check.ps1** – Salvar erros de lint em Downloads

## 🔄 Fluxo de Alta Produtividade
1. Planejar no TimeTracker
2. Criar branch (git checkout -b feat/nome)
3. Editar com Cursor / Aider
4. Testar (pytest)
5. Commitar (pre-commit roda automático)
6. Push (GitHub Actions valida)
7. Merge + Deploy (script ou SSH)

**Este documento deve ser consultado antes de iniciar qualquer tarefa.**
