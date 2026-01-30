-- Sichelgaita.AI File Management Schema
-- Migration 001: Files and Processed Data Tables

-- Create ENUM types
CREATE TYPE file_type_enum AS ENUM ('csv', 'excel', 'pdf', 'image');
CREATE TYPE file_status_enum AS ENUM ('uploading', 'processing', 'completed', 'failed');

-- Files table: stores file metadata and processing status
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID NULL,
    filename TEXT NOT NULL,
    file_type file_type_enum NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    status file_status_enum NOT NULL DEFAULT 'uploading',
    ai_summary TEXT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Processed data table: stores cleaned and normalized data
CREATE TABLE processed_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    cleaned_data JSONB NOT NULL,
    data_schema JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_files_created_at ON files(created_at DESC);
CREATE INDEX idx_processed_data_file_id ON processed_data(file_id);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_files_updated_at
    BEFORE UPDATE ON files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE processed_data ENABLE ROW LEVEL SECURITY;

-- Users can only view their own files
CREATE POLICY "Users can view own files"
    ON files FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own files
CREATE POLICY "Users can insert own files"
    ON files FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own files
CREATE POLICY "Users can update own files"
    ON files FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can delete their own files
CREATE POLICY "Users can delete own files"
    ON files FOR DELETE
    USING (auth.uid() = user_id);

-- Users can view processed data for their own files
CREATE POLICY "Users can view own processed data"
    ON processed_data FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM files
            WHERE files.id = processed_data.file_id
            AND files.user_id = auth.uid()
        )
    );

-- Users can insert processed data for their own files
CREATE POLICY "Users can insert own processed data"
    ON processed_data FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM files
            WHERE files.id = processed_data.file_id
            AND files.user_id = auth.uid()
        )
    );

-- Service role bypass (for backend operations)
CREATE POLICY "Service role has full access to files"
    ON files FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has full access to processed_data"
    ON processed_data FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
