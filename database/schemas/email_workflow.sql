-- Schema para Workflow de Aprovação de Emails
-- Atualiza a tabela email_cache para suportar workflow de aprovação

-- Enum para status do workflow
CREATE TYPE email_workflow_status AS ENUM (
    'received',           -- Email recebido, aguardando primeira análise
    'analyzed',          -- Analisado pela IA, aguardando revisão do usuário
    'approved_content',  -- Usuário aprovou o conteúdo gerado
    'ready_publish',     -- Pronto para publicação, aguardando aprovação final
    'published',         -- Publicado no WordPress
    'rejected',          -- Rejeitado pelo usuário
    'archived'           -- Arquivado (emails antigos)
);

-- Atualizar tabela email_cache
ALTER TABLE email_cache 
DROP CONSTRAINT IF EXISTS email_cache_status_check;

ALTER TABLE email_cache 
ALTER COLUMN status TYPE email_workflow_status 
USING status::email_workflow_status;

-- Adicionar colunas para workflow
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS workflow_stage email_workflow_status DEFAULT 'received';
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS ai_analysis JSONB;
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS user_feedback JSONB;
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS approval_history JSONB DEFAULT '[]'::jsonb;
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS assigned_to UUID;
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 3; -- 1=alta, 2=média, 3=baixa
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS tags TEXT[];
ALTER TABLE email_cache ADD COLUMN IF NOT EXISTS is_auto_process BOOLEAN DEFAULT true; -- false para emails antigos

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_email_cache_workflow_stage ON email_cache(workflow_stage);
CREATE INDEX IF NOT EXISTS idx_email_cache_priority ON email_cache(priority);
CREATE INDEX IF NOT EXISTS idx_email_cache_assigned_to ON email_cache(assigned_to);
CREATE INDEX IF NOT EXISTS idx_email_cache_auto_process ON email_cache(is_auto_process);

-- Tabela para histórico de ações do workflow
CREATE TABLE IF NOT EXISTS email_workflow_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID REFERENCES email_cache(id),
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    from_stage email_workflow_status,
    to_stage email_workflow_status,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_workflow_history_email_id ON email_workflow_history(email_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_user_id ON email_workflow_history(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_created_at ON email_workflow_history(created_at);

-- Função para registrar ações do workflow
CREATE OR REPLACE FUNCTION log_workflow_action(
    p_email_id UUID,
    p_user_id UUID,
    p_action VARCHAR(50),
    p_from_stage email_workflow_status,
    p_to_stage email_workflow_status,
    p_notes TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    history_id UUID;
BEGIN
    INSERT INTO email_workflow_history (
        email_id, user_id, action, from_stage, to_stage, notes, metadata
    ) VALUES (
        p_email_id, p_user_id, p_action, p_from_stage, p_to_stage, p_notes, p_metadata
    ) RETURNING id INTO history_id;
    
    RETURN history_id;
END;
$$ LANGUAGE plpgsql;

-- View para dashboard de emails
CREATE OR REPLACE VIEW email_dashboard AS
SELECT 
    ec.id,
    ec.email_hash,
    ec.sender,
    ec.subject,
    ec.workflow_stage,
    ec.priority,
    ec.tags,
    ec.is_auto_process,
    ec.assigned_to,
    ec.received_at,
    ec.updated_at,
    ec.ai_analysis->>'category' as ai_category,
    ec.ai_analysis->>'confidence' as ai_confidence,
    ec.user_feedback->>'rating' as user_rating,
    ec.user_feedback->>'notes' as user_notes,
    CASE 
        WHEN ec.workflow_stage = 'received' THEN 'Aguardando Análise'
        WHEN ec.workflow_stage = 'analyzed' THEN 'Aguardando Revisão'
        WHEN ec.workflow_stage = 'approved_content' THEN 'Conteúdo Aprovado'
        WHEN ec.workflow_stage = 'ready_publish' THEN 'Pronto para Publicar'
        WHEN ec.workflow_stage = 'published' THEN 'Publicado'
        WHEN ec.workflow_stage = 'rejected' THEN 'Rejeitado'
        WHEN ec.workflow_stage = 'archived' THEN 'Arquivado'
    END as stage_display,
    (
        SELECT COUNT(*) 
        FROM email_workflow_history ewh 
        WHERE ewh.email_id = ec.id
    ) as action_count
FROM email_cache ec
ORDER BY 
    CASE ec.priority WHEN 1 THEN 1 WHEN 2 THEN 2 ELSE 3 END,
    ec.received_at DESC;

-- Função para estatísticas do dashboard
CREATE OR REPLACE FUNCTION get_email_workflow_stats(
    p_user_id UUID DEFAULT NULL,
    p_days_back INTEGER DEFAULT 30
) RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_emails', COUNT(*),
        'by_stage', jsonb_object_agg(workflow_stage, stage_count),
        'by_priority', jsonb_object_agg(priority_level, priority_count),
        'pending_review', SUM(CASE WHEN workflow_stage IN ('received', 'analyzed') THEN 1 ELSE 0 END),
        'ready_to_publish', SUM(CASE WHEN workflow_stage = 'ready_publish' THEN 1 ELSE 0 END),
        'published_today', SUM(CASE WHEN workflow_stage = 'published' AND DATE(updated_at) = CURRENT_DATE THEN 1 ELSE 0 END)
    ) INTO result
    FROM (
        SELECT 
            workflow_stage,
            CASE priority WHEN 1 THEN 'alta' WHEN 2 THEN 'media' ELSE 'baixa' END as priority_level,
            COUNT(*) OVER (PARTITION BY workflow_stage) as stage_count,
            COUNT(*) OVER (PARTITION BY priority) as priority_count
        FROM email_cache 
        WHERE received_at >= CURRENT_DATE - INTERVAL '%s days'
            AND (p_user_id IS NULL OR assigned_to = p_user_id)
    ) stats;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql; 