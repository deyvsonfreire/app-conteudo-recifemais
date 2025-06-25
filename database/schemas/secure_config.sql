-- Tabela para armazenar configurações seguras/sensíveis
CREATE TABLE IF NOT EXISTS secure_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    encrypted_value TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca rápida por chave
CREATE INDEX IF NOT EXISTS idx_secure_config_key ON secure_config(key);

-- RLS (Row Level Security) para proteger dados sensíveis
ALTER TABLE secure_config ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas via service key
CREATE POLICY "secure_config_policy" ON secure_config
    FOR ALL USING (auth.role() = 'service_role');

-- Comentários para documentação
COMMENT ON TABLE secure_config IS 'Armazena configurações sensíveis como credenciais OAuth, chaves API, etc.';
COMMENT ON COLUMN secure_config.key IS 'Chave única da configuração';
COMMENT ON COLUMN secure_config.encrypted_value IS 'Valor criptografado da configuração';
COMMENT ON COLUMN secure_config.description IS 'Descrição da configuração'; 