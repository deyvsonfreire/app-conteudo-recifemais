-- Função para busca de documentos similares usando pgvector
-- Requer extensão pgvector habilitada no Supabase

-- Habilitar extensão pgvector (se não estiver habilitada)
CREATE EXTENSION IF NOT EXISTS vector;

-- Função para busca de similaridade
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  content_text text,
  source_url text,
  topic varchar(100),
  category_recifemais varchar(50),
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    kb.content_text,
    kb.source_url,
    kb.topic,
    kb.category_recifemais,
    kb.metadata,
    1 - (kb.embedding <=> query_embedding) AS similarity
  FROM knowledge_base kb
  WHERE 1 - (kb.embedding <=> query_embedding) > match_threshold
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Índice para otimizar busca por similaridade
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Comentários para documentação
COMMENT ON FUNCTION match_documents IS 'Busca documentos similares usando embeddings com pgvector';
COMMENT ON INDEX idx_knowledge_base_embedding IS 'Índice otimizado para busca por similaridade de embeddings'; 