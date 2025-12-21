-- Q&A Pairs Migration
-- Add table for user-uploaded expected interview questions and answers

-- Q&A Pairs table
CREATE TABLE public.qa_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    question_normalized TEXT NOT NULL, -- Lowercase, trimmed for semantic matching
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('behavioral', 'technical', 'situational', 'general')),
    source VARCHAR(50) DEFAULT 'manual' CHECK (source IN ('manual', 'bulk_upload')),
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_qa_pairs_user ON public.qa_pairs(user_id);
CREATE INDEX idx_qa_pairs_user_type ON public.qa_pairs(user_id, question_type);
CREATE INDEX idx_qa_pairs_normalized ON public.qa_pairs(question_normalized);

-- Enable Row Level Security
ALTER TABLE public.qa_pairs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for qa_pairs (user isolation)
CREATE POLICY "Users can view own qa pairs" ON public.qa_pairs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own qa pairs" ON public.qa_pairs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own qa pairs" ON public.qa_pairs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own qa pairs" ON public.qa_pairs
    FOR DELETE USING (auth.uid() = user_id);

-- Trigger for updated_at
CREATE TRIGGER update_qa_pairs_updated_at BEFORE UPDATE ON public.qa_pairs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically normalize question on insert/update
CREATE OR REPLACE FUNCTION normalize_qa_question()
RETURNS TRIGGER AS $$
BEGIN
    NEW.question_normalized = LOWER(TRIM(NEW.question));
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER normalize_qa_question_trigger
    BEFORE INSERT OR UPDATE ON public.qa_pairs
    FOR EACH ROW EXECUTE FUNCTION normalize_qa_question();
