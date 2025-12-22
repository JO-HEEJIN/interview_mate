-- Interview session tracking for memory and export
-- Tracks interview sessions and all Q&A exchanges during the session

-- Interview sessions table
CREATE TABLE IF NOT EXISTS public.interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,

    -- Session metadata
    title VARCHAR(255) DEFAULT 'Interview Session',
    session_type VARCHAR(50) DEFAULT 'practice' CHECK (session_type IN ('practice', 'mock', 'real')),

    -- Session status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'abandoned')),

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN ended_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (ended_at - started_at))::INTEGER
            ELSE NULL
        END
    ) STORED,

    -- Statistics
    question_count INTEGER DEFAULT 0,

    -- Session notes and metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Session messages (Q&A pairs during interview)
CREATE TABLE IF NOT EXISTS public.session_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.interview_sessions(id) ON DELETE CASCADE,

    -- Message content
    role VARCHAR(50) NOT NULL CHECK (role IN ('interviewer', 'candidate', 'system')),
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('question', 'answer', 'transcription', 'note')),
    content TEXT NOT NULL,

    -- Metadata
    question_type VARCHAR(50), -- behavioral, technical, situational, general
    source VARCHAR(50), -- prepared_qa, ai_generated, manual
    matched_qa_pair_id UUID REFERENCES public.qa_pairs(id) ON DELETE SET NULL,

    -- Examples used in this answer (to avoid repetition)
    examples_used JSONB DEFAULT '[]', -- ["Project A", "Leadership at Company X", ...]

    -- Timing
    message_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sequence_number INTEGER, -- Order in conversation

    -- Quality/feedback
    confidence_score FLOAT, -- User's self-rating (0-5)
    interviewer_feedback TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user ON public.interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_status ON public.interview_sessions(status);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_started ON public.interview_sessions(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_session_messages_session ON public.session_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_session_messages_timestamp ON public.session_messages(message_timestamp);
CREATE INDEX IF NOT EXISTS idx_session_messages_role ON public.session_messages(role);

-- RLS Policies
ALTER TABLE public.interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_messages ENABLE ROW LEVEL SECURITY;

-- Users can only access their own sessions
CREATE POLICY interview_sessions_user_policy ON public.interview_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Users can only access messages from their own sessions
CREATE POLICY session_messages_user_policy ON public.session_messages
    FOR ALL USING (
        session_id IN (
            SELECT id FROM public.interview_sessions WHERE user_id = auth.uid()
        )
    );

-- Helper function: Get session history (for Claude context)
CREATE OR REPLACE FUNCTION get_session_history(session_id_param UUID)
RETURNS TABLE (
    role VARCHAR(50),
    message_type VARCHAR(50),
    content TEXT,
    examples_used JSONB,
    message_timestamp TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.role,
        sm.message_type,
        sm.content,
        sm.examples_used,
        sm.message_timestamp
    FROM public.session_messages sm
    WHERE sm.session_id = session_id_param
    ORDER BY sm.sequence_number, sm.message_timestamp;
END;
$$ LANGUAGE plpgsql STABLE;

-- Helper function: Get all examples used in session (to avoid repetition)
CREATE OR REPLACE FUNCTION get_session_examples(session_id_param UUID)
RETURNS TABLE (
    example TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT jsonb_array_elements_text(sm.examples_used) AS example
    FROM public.session_messages sm
    WHERE sm.session_id = session_id_param
        AND sm.role = 'candidate'
        AND sm.message_type = 'answer'
        AND sm.examples_used IS NOT NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: End session and update statistics
CREATE OR REPLACE FUNCTION end_interview_session(session_id_param UUID)
RETURNS public.interview_sessions AS $$
DECLARE
    session_record public.interview_sessions;
BEGIN
    UPDATE public.interview_sessions
    SET
        status = 'completed',
        ended_at = NOW(),
        question_count = (
            SELECT COUNT(*)
            FROM public.session_messages
            WHERE session_id = session_id_param
                AND role = 'interviewer'
                AND message_type = 'question'
        ),
        updated_at = NOW()
    WHERE id = session_id_param
    RETURNING * INTO session_record;

    RETURN session_record;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE public.interview_sessions IS 'Tracks interview practice sessions with timing and metadata';
COMMENT ON TABLE public.session_messages IS 'Stores all Q&A exchanges during interview sessions with example tracking';
COMMENT ON FUNCTION get_session_history IS 'Retrieve full conversation history for a session (for Claude context)';
COMMENT ON FUNCTION get_session_examples IS 'Get all examples already used in a session to avoid repetition';
COMMENT ON FUNCTION end_interview_session IS 'Mark session as completed and update statistics';
