-- ============================================================
-- Sprint 5: Tabelas de Consentimento, Auditoria e Agentes
-- Executar no banco research_agent
-- ============================================================


-- ============================================================
-- Tabela: consents
-- Registro de consentimentos LGPD (append-only)
-- ============================================================
CREATE TABLE IF NOT EXISTS consents (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id       UUID         NOT NULL,
    conversation_id  UUID,
    type             VARCHAR(32)  NOT NULL,   -- initial, research_participation, personal_data,
                                              --   sensitive_data, human_handoff, data_retention
    status           VARCHAR(16)  NOT NULL,   -- pending, granted, denied
    legal_basis      VARCHAR(32)  NOT NULL DEFAULT 'consent',
    purpose          VARCHAR(128),
    channel_message_id VARCHAR(128),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_consents_contact_id      ON consents(contact_id);
CREATE INDEX IF NOT EXISTS ix_consents_conversation_id ON consents(conversation_id);
CREATE INDEX IF NOT EXISTS ix_consents_type            ON consents(type);


-- ============================================================
-- Tabela: audit_logs
-- Registro de eventos críticos (append-only, imutável)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event           VARCHAR(64) NOT NULL,
    actor           VARCHAR(32) NOT NULL,
    entity          VARCHAR(32) NOT NULL,
    entity_id       UUID        NOT NULL,
    action          VARCHAR(32) NOT NULL,
    criticality     VARCHAR(8)  NOT NULL,
    conversation_id UUID,
    context         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
    -- O Python (audit_service.py) grava created_at com offset de Brasília/DF.
    -- TIMESTAMPTZ converte para UTC internamente; use a view abaixo para exibir
    -- os logs já convertidos para America/Sao_Paulo.
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_event           ON audit_logs(event);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_id       ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_conversation_id ON audit_logs(conversation_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at      ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS ix_audit_logs_criticality     ON audit_logs(criticality);


-- ============================================================
-- View: audit_logs_brasilia
-- Exibe audit_logs com created_at convertido para Brasília/DF.
-- Use esta view para consultas operacionais e relatórios.
-- ============================================================
CREATE OR REPLACE VIEW audit_logs_brasilia AS
SELECT
    id,
    event,
    actor,
    entity,
    entity_id,
    action,
    criticality,
    conversation_id,
    context,
    created_at AT TIME ZONE 'America/Sao_Paulo' AS created_at_brasilia
FROM audit_logs;


-- ============================================================
-- NOVO — Tabela: research_agents
-- Agentes pesquisadores humanos disponíveis para handoff
-- ============================================================
CREATE TABLE IF NOT EXISTS research_agents (
    id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(120) NOT NULL,
    phone      VARCHAR(20)  NOT NULL UNIQUE,   -- formato E.164, ex: +5561999990001
    active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_research_agents_phone  ON research_agents(phone);
CREATE INDEX IF NOT EXISTS ix_research_agents_active ON research_agents(active);

-- Para desativar um agente sem apagar histórico:
--   UPDATE research_agents SET active = false WHERE id = '<uuid>';

-- Exemplo de INSERT:
-- INSERT INTO research_agents (name, phone) VALUES
--   ('Maria Silva',  '+5561999990001'),
--   ('João Pereira', '+5561999990002');
