CREATE TABLE IF NOT EXISTS tutor.lab_baseline (
    baseline_id INTEGER PRIMARY KEY DEFAULT 1 CHECK (baseline_id = 1),
    ddl TEXT NOT NULL,
    seed_sql TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

