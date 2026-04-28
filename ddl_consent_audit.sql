-- Sprint 5: Tabelas de Consentimento e Auditoria
CREATE TABLE IF NOT EXISTS consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL,
    conversation_id UUID,
    type VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL,
    legal_basis VARCHAR(32) NOT NULL DEFAULT 'consent',
    purpose VARCHAR(128),
    channel_message_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_consents_contact_id ON consents(contact_id);
CREATE INDEX IF NOT EXISTS ix_consents_conversation_id ON consents(conversation_id);
CREATE INDEX IF NOT EXISTS ix_consents_type ON consents(type);
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event VARCHAR(64) NOT NULL,
    actor VARCHAR(32) NOT NULL,
    entity VARCHAR(32) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(32) NOT NULL,
    criticality VARCHAR(8) NOT NULL,
    conversation_id UUID,
    context JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_audit_logs_event ON audit_logs(event);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_conversation_id ON audit_logs(conversation_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS ix_audit_logs_criticality ON audit_logs(criticality);
