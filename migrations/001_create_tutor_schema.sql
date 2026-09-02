CREATE SCHEMA IF NOT EXISTS tutor;

CREATE TABLE IF NOT EXISTS tutor.learning_session (
    session_id UUID PRIMARY KEY,
    topic TEXT NOT NULL,
    goal TEXT,
    phase TEXT NOT NULL DEFAULT 'INTENT',
    status TEXT NOT NULL DEFAULT 'active',
    scenario JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tutor.learning_concept (
    concept_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES tutor.learning_session(session_id) ON DELETE CASCADE,
    concept_key TEXT NOT NULL,
    name TEXT NOT NULL,
    mastery NUMERIC(4,3) NOT NULL DEFAULT 0 CHECK (mastery BETWEEN 0 AND 1),
    confidence TEXT NOT NULL DEFAULT 'low' CHECK (confidence IN ('low', 'medium', 'high')),
    misconception TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, concept_key)
);

CREATE TABLE IF NOT EXISTS tutor.learning_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES tutor.learning_session(session_id) ON DELETE CASCADE,
    concept_id BIGINT REFERENCES tutor.learning_concept(concept_id) ON DELETE SET NULL,
    evidence_type TEXT NOT NULL,
    difficulty TEXT,
    correctness NUMERIC(4,3),
    reasoning_quality NUMERIC(4,3),
    attempts INTEGER NOT NULL DEFAULT 1 CHECK (attempts > 0),
    assistance TEXT,
    raw_evidence JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS learning_evidence_session_created_idx
    ON tutor.learning_evidence (session_id, created_at);

CREATE TABLE IF NOT EXISTS tutor.learning_event (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES tutor.learning_session(session_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS learning_event_session_created_idx
    ON tutor.learning_event (session_id, created_at);

