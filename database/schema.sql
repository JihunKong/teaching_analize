-- AIBOA Database Schema
-- User Role-based System with Enhanced Features

-- Enable UUID extension for better security
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- User Management Schema
-- ============================================

-- User Roles Definition
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial roles
INSERT INTO user_roles (name, display_name, description, permissions) VALUES
('admin', 'Administrator', 'Full system access and user management', 
 '{"users": ["create", "read", "update", "delete"], "analytics": ["read"], "system": ["configure"], "data": ["read_all", "export"]}'),
('coach', 'Teaching Coach', 'Dashboard access and history viewing', 
 '{"own_data": ["create", "read"], "dashboard": ["read"], "reports": ["generate"], "history": ["read"], "compare": ["read"]}'),
('regular_user', 'Regular User', 'Basic transcription and analysis workflow', 
 '{"transcription": ["create"], "analysis": ["create"], "results": ["read_own"], "workflow": ["unified"]}');

-- Main Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'regular_user' REFERENCES user_roles(name),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    profile_image_url TEXT,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- User Sessions for JWT management
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    device_info JSONB DEFAULT '{}',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP
);

-- Password Reset Tokens
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Enhanced Transcription Schema
-- ============================================

-- Update transcription_jobs table for multi-user support
CREATE TABLE transcription_jobs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    source_type VARCHAR(50) NOT NULL, -- 'youtube', 'upload'
    source_url TEXT,
    filename TEXT,
    language VARCHAR(10) DEFAULT 'ko',
    export_format VARCHAR(20) DEFAULT 'json',
    file_size BIGINT,
    duration_seconds INTEGER,
    transcript_text TEXT,
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    shared_with JSONB DEFAULT '[]'
);

-- ============================================
-- Enhanced Analysis Schema  
-- ============================================

-- Update analysis_results table for multi-user support
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transcription_job_id INTEGER REFERENCES transcription_jobs(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
    framework VARCHAR(50) NOT NULL DEFAULT 'cbil',
    input_text TEXT NOT NULL,
    results JSONB NOT NULL,
    overall_score DECIMAL(5,2),
    primary_level VARCHAR(100),
    processing_time_seconds DECIMAL(8,3),
    word_count INTEGER,
    sentence_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    shared_with JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

-- ============================================
-- Workflow Integration Schema
-- ============================================

-- Unified Workflow Sessions (for integrated transcription + analysis)
CREATE TABLE workflow_sessions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'initiated', -- initiated, transcribing, analyzing, completed, failed
    transcription_job_id INTEGER REFERENCES transcription_jobs(id),
    analysis_result_id INTEGER REFERENCES analysis_results(id),
    progress_percentage INTEGER DEFAULT 0,
    transcription_progress INTEGER DEFAULT 0,
    analysis_progress INTEGER DEFAULT 0,
    estimated_completion_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    error_details TEXT
);

-- ============================================
-- Data Access & Permissions
-- ============================================

-- Fine-grained data access permissions
CREATE TABLE data_access_permissions (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL, -- 'transcription', 'analysis', 'workflow', 'report'
    resource_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    permission_type VARCHAR(50) NOT NULL, -- 'read', 'write', 'share', 'delete'
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(resource_type, resource_id, user_id, permission_type)
);

-- ============================================
-- Activity Logging & Analytics
-- ============================================

-- User Activity Logs for admin monitoring
CREATE TABLE user_activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);

-- Usage Statistics for analytics
CREATE TABLE usage_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    aggregation_period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, metric_name, aggregation_period, period_start)
);

-- ============================================
-- Reports & Exports
-- ============================================

-- Generated Reports tracking
CREATE TABLE generated_reports (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path TEXT,
    file_size BIGINT,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'generating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    downloaded_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- ============================================
-- System Configuration
-- ============================================

-- System settings and configuration
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('max_file_size_mb', '500', 'Maximum file size for uploads in MB', false),
('supported_languages', '["ko", "en", "auto"]', 'Supported transcription languages', true),
('default_analysis_framework', '"cbil"', 'Default analysis framework', true),
('session_timeout_hours', '24', 'User session timeout in hours', false),
('max_concurrent_jobs', '5', 'Maximum concurrent jobs per user', false);

-- ============================================
-- Indexes for Performance
-- ============================================

-- User table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Session indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Transcription indexes
CREATE INDEX idx_transcription_jobs_user_id ON transcription_jobs(user_id);
CREATE INDEX idx_transcription_jobs_status ON transcription_jobs(status);
CREATE INDEX idx_transcription_jobs_created_at ON transcription_jobs(created_at);

-- Analysis indexes
CREATE INDEX idx_analysis_results_user_id ON analysis_results(user_id);
CREATE INDEX idx_analysis_results_transcription_job_id ON analysis_results(transcription_job_id);
CREATE INDEX idx_analysis_results_created_at ON analysis_results(created_at);

-- Workflow indexes
CREATE INDEX idx_workflow_sessions_user_id ON workflow_sessions(user_id);
CREATE INDEX idx_workflow_sessions_status ON workflow_sessions(status);
CREATE INDEX idx_workflow_sessions_created_at ON workflow_sessions(created_at);

-- Activity logs indexes
CREATE INDEX idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_logs_action ON user_activity_logs(action);
CREATE INDEX idx_user_activity_logs_created_at ON user_activity_logs(created_at);

-- ============================================
-- Functions & Triggers
-- ============================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log user activities
CREATE OR REPLACE FUNCTION log_user_activity()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_activity_logs (user_id, action, resource_type, resource_id, details)
    VALUES (
        COALESCE(NEW.user_id, OLD.user_id),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        row_to_json(COALESCE(NEW, OLD))
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Apply activity logging to important tables
CREATE TRIGGER log_transcription_activity AFTER INSERT OR UPDATE OR DELETE ON transcription_jobs
    FOR EACH ROW EXECUTE FUNCTION log_user_activity();

CREATE TRIGGER log_analysis_activity AFTER INSERT OR UPDATE OR DELETE ON analysis_results
    FOR EACH ROW EXECUTE FUNCTION log_user_activity();

-- ============================================
-- Initial Admin User Creation
-- ============================================

-- This will be handled by the authentication service to properly hash passwords
-- The admin user creation is commented out here and will be done programmatically

-- ============================================
-- Views for Common Queries
-- ============================================

-- User dashboard summary view
CREATE VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.role,
    COUNT(DISTINCT tj.id) as total_transcriptions,
    COUNT(DISTINCT ar.id) as total_analyses,
    COUNT(DISTINCT ws.id) as total_workflows,
    AVG(ar.overall_score) as avg_analysis_score,
    MAX(tj.created_at) as last_transcription_date,
    MAX(ar.created_at) as last_analysis_date
FROM users u
LEFT JOIN transcription_jobs tj ON u.id = tj.user_id
LEFT JOIN analysis_results ar ON u.id = ar.user_id
LEFT JOIN workflow_sessions ws ON u.id = ws.user_id
GROUP BY u.id, u.full_name, u.role;

-- System statistics view for admin
CREATE VIEW system_statistics AS
SELECT 
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT CASE WHEN u.role = 'regular_user' THEN u.id END) as regular_users,
    COUNT(DISTINCT CASE WHEN u.role = 'coach' THEN u.id END) as coach_users,
    COUNT(DISTINCT CASE WHEN u.role = 'admin' THEN u.id END) as admin_users,
    COUNT(DISTINCT tj.id) as total_transcriptions,
    COUNT(DISTINCT ar.id) as total_analyses,
    COUNT(DISTINCT ws.id) as total_workflows,
    AVG(ar.overall_score) as avg_system_score
FROM users u
LEFT JOIN transcription_jobs tj ON u.id = tj.user_id
LEFT JOIN analysis_results ar ON u.id = ar.user_id
LEFT JOIN workflow_sessions ws ON u.id = ws.user_id;

-- ============================================
-- Comments and Documentation
-- ============================================

COMMENT ON TABLE users IS 'Main user authentication and profile table with role-based access';
COMMENT ON TABLE user_roles IS 'Defines available user roles and their permissions';
COMMENT ON TABLE workflow_sessions IS 'Tracks unified transcription + analysis workflows for regular users';
COMMENT ON TABLE data_access_permissions IS 'Fine-grained permissions for data sharing between users';
COMMENT ON TABLE user_activity_logs IS 'Audit trail for user actions and system usage';
COMMENT ON TABLE usage_statistics IS 'Aggregated usage metrics for analytics and reporting';

-- Schema version tracking
INSERT INTO system_settings (setting_key, setting_value, description) 
VALUES ('schema_version', '"1.0.0"', 'Database schema version for migration tracking');