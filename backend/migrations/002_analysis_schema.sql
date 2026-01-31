-- Analysis types enum
CREATE TYPE analysis_type_enum AS ENUM ('trend', 'anomaly', 'executive_summary');

-- Analysis results table
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    analysis_type analysis_type_enum NOT NULL,
    insights JSONB NOT NULL,
    chart_config JSONB NULL,
    anomalies JSONB NULL,
    key_metrics JSONB NULL,
    recommendations JSONB NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_analysis_file_id ON analysis_results(file_id);
CREATE INDEX idx_analysis_type ON analysis_results(analysis_type);
CREATE INDEX idx_analysis_created_at ON analysis_results(created_at DESC);

-- RLS Policies
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own analysis"
    ON analysis_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM files
            WHERE files.id = analysis_results.file_id
            AND files.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own analysis"
    ON analysis_results FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM files
            WHERE files.id = analysis_results.file_id
            AND files.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role has full access to analysis"
    ON analysis_results FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
