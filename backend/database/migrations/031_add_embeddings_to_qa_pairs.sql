-- Add embedding column to qa_pairs for semantic similarity matching
-- Using pgvector extension for efficient vector operations

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column (OpenAI embeddings are 1536 dimensions for text-embedding-3-small)
ALTER TABLE public.qa_pairs
    ADD COLUMN IF NOT EXISTS question_embedding vector(1536),
    ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(50) DEFAULT 'text-embedding-3-small',
    ADD COLUMN IF NOT EXISTS embedding_created_at TIMESTAMP WITH TIME ZONE;

-- Create index for fast similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_qa_pairs_embedding ON public.qa_pairs
    USING ivfflat (question_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Add comment
COMMENT ON COLUMN public.qa_pairs.question_embedding IS 'OpenAI embedding vector for semantic similarity matching';
COMMENT ON COLUMN public.qa_pairs.embedding_model IS 'OpenAI model used for embedding generation';
COMMENT ON COLUMN public.qa_pairs.embedding_created_at IS 'Timestamp when embedding was generated';

-- Create function to find similar Q&A pairs using semantic similarity
CREATE OR REPLACE FUNCTION find_similar_qa_pairs(
    user_id_param UUID,
    query_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.80,
    max_results INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    question TEXT,
    answer TEXT,
    question_type VARCHAR(50),
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        qa.id,
        qa.question,
        qa.answer,
        qa.question_type,
        1 - (qa.question_embedding <=> query_embedding) AS similarity
    FROM public.qa_pairs qa
    WHERE qa.user_id = user_id_param
        AND qa.question_embedding IS NOT NULL
        AND 1 - (qa.question_embedding <=> query_embedding) >= similarity_threshold
    ORDER BY qa.question_embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION find_similar_qa_pairs IS 'Find Q&A pairs semantically similar to query embedding using cosine similarity';
