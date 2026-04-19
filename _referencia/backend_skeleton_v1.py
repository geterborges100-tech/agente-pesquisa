"""
MANIFESTO TÉCNICO V1 - BACKEND INSTAGRAM AGENT
Este arquivo consolida a arquitetura aprovada para evitar múltiplas leituras.
"""

# ESTRUTURA DE PASTAS APROVADA:
# app/
#  ├── api/v1/ (router.py, webhooks.py, contacts.py)
#  ├── core/ (config.py, exceptions.py, security.py)
#  ├── db/ (base.py, session.py)
#  ├── models/ (contact.py, conversation.py, event.py)
#  ├── repositories/ (base.py, contact_repo.py, conversation_repo.py)
#  └── services/ (webhook_service.py, ai_service.py)

# CONFIGURAÇÕES CORE
# - FastAPI + SQLAlchemy 2.0 Async + Pydantic V2
# - PostgreSQL com UUID (gen_random_uuid)
# - Padrão Repository para desacoplamento de banco

# --- MÓDULO DB BASE ---
# class Base(DeclarativeBase): pass

# --- MODEL: CONTACT (Campos Críticos) ---
# id: UUID, account_id: UUID, external_user_id: str, 
# consent_status: enum, segment: str, lead_score: numeric(5,2)

# --- MODEL: CONVERSATION (Campos Críticos) ---
# id: UUID, contact_id: FK(contacts.id), status: enum, 
# current_node_key: str, last_message_at: datetime

# --- REPOSITORY BASE (Assinaturas) ---
# get_by_id(id: UUID), list_all(skip, limit), create(dict), 
# update(id, dict), delete(id)

# --- WEBHOOK (Regras Meta) ---
# GET /webhooks/meta/instagram -> Valida hub.verify_token
# POST /webhooks/meta/instagram -> Recebe JSON e delega para webhook_service