-- AIBOA Teaching Analysis System Database Schema
-- Version: 1.0.0
-- Date: 2024

-- ================================================
-- Transcription Service Tables
-- ================================================

-- Transcription Jobs Table
CREATE TABLE IF NOT EXISTS transcription_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    file_name VARCHAR(255),
    file_size INTEGER,
    duration FLOAT,
    language VARCHAR(10) DEFAULT 'ko',
    method VARCHAR(50) DEFAULT 'whisper',
    error_message TEXT,
    progress INTEGER DEFAULT 0,
    transcript_path VARCHAR(500),
    cost_estimate FLOAT,
    user_id VARCHAR(255)
);

-- Indexes for transcription_jobs
CREATE INDEX IF NOT EXISTS idx_transcription_job_id ON transcription_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_transcription_status ON transcription_jobs(status);
CREATE INDEX IF NOT EXISTS idx_transcription_created_at ON transcription_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_transcription_user_id ON transcription_jobs(user_id);

-- ================================================
-- Analysis Service Tables
-- ================================================

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    transcript_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    teacher_name VARCHAR(255),
    subject VARCHAR(255),
    grade_level VARCHAR(50),
    class_duration INTEGER,
    cbil_distribution JSONB,
    average_cbil_level FLOAT,
    teacher_talk_ratio FLOAT,
    student_talk_ratio FLOAT,
    interaction_count INTEGER,
    total_questions INTEGER,
    open_questions INTEGER,
    closed_questions INTEGER,
    detailed_analysis JSONB,
    recommendations JSONB,
    report_path VARCHAR(500),
    visual_report_path VARCHAR(500)
);

-- Indexes for analysis_results
CREATE INDEX IF NOT EXISTS idx_analysis_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_transcript_id ON analysis_results(transcript_id);
CREATE INDEX IF NOT EXISTS idx_analysis_teacher_name ON analysis_results(teacher_name);
CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON analysis_results(created_at);

-- Teacher Profiles Table
CREATE TABLE IF NOT EXISTS teacher_profiles (
    id SERIAL PRIMARY KEY,
    teacher_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subjects JSONB,
    grade_levels JSONB,
    years_experience INTEGER,
    total_analyses INTEGER DEFAULT 0,
    average_cbil FLOAT,
    improvement_trend JSONB,
    preferred_language VARCHAR(10) DEFAULT 'ko',
    notification_settings JSONB
);

-- Indexes for teacher_profiles
CREATE INDEX IF NOT EXISTS idx_teacher_id ON teacher_profiles(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_email ON teacher_profiles(email);
CREATE INDEX IF NOT EXISTS idx_teacher_name ON teacher_profiles(name);

-- ================================================
-- Session Management Tables
-- ================================================

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_session_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_session_active ON user_sessions(is_active);

-- ================================================
-- Audit and Logging Tables
-- ================================================

-- API Request Logs
CREATE TABLE IF NOT EXISTS api_request_logs (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    service VARCHAR(50),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    user_id VARCHAR(255),
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON api_request_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_request_logs_service ON api_request_logs(service);
CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON api_request_logs(user_id);

-- ================================================
-- Views for Analytics
-- ================================================

-- Daily Analysis Summary View
CREATE OR REPLACE VIEW daily_analysis_summary AS
SELECT 
    DATE(created_at) as analysis_date,
    COUNT(*) as total_analyses,
    AVG(average_cbil_level) as avg_cbil_level,
    AVG(teacher_talk_ratio) as avg_teacher_talk_ratio,
    AVG(interaction_count) as avg_interactions
FROM analysis_results
GROUP BY DATE(created_at)
ORDER BY analysis_date DESC;

-- Teacher Performance View
CREATE OR REPLACE VIEW teacher_performance AS
SELECT 
    teacher_name,
    COUNT(*) as total_analyses,
    AVG(average_cbil_level) as avg_cbil_level,
    AVG(teacher_talk_ratio) as avg_teacher_talk_ratio,
    AVG(student_talk_ratio) as avg_student_talk_ratio,
    MIN(created_at) as first_analysis,
    MAX(created_at) as last_analysis
FROM analysis_results
WHERE teacher_name IS NOT NULL
GROUP BY teacher_name
ORDER BY total_analyses DESC;

-- ================================================
-- Functions and Triggers
-- ================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_transcription_jobs_updated_at 
    BEFORE UPDATE ON transcription_jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- Initial Data
-- ================================================

-- Insert default CBIL level descriptions (for reference)
CREATE TABLE IF NOT EXISTS cbil_levels (
    level INTEGER PRIMARY KEY,
    name VARCHAR(100),
    name_ko VARCHAR(100),
    description TEXT,
    description_ko TEXT,
    examples TEXT,
    characteristics TEXT
);

INSERT INTO cbil_levels (level, name, name_ko, description, description_ko, examples, characteristics)
VALUES 
    (1, 'Simple Confirmation', '단순 확인', 'Yes/No answers', '단순한 예/아니오 대답', '네, 아니오, 맞아요', '5 words or less, simple acknowledgment'),
    (2, 'Fact Recall', '사실 회상', 'Simple information repetition', '단순한 정보 반복', '책상입니다, 3 더하기 2는 5입니다', '5-15 words, direct repetition of facts'),
    (3, 'Concept Explanation', '개념 설명', 'Restating in own words', '자신의 말로 다시 설명', '이것은 물체가 떨어지는 현상을 말해요', '15-30 words, paraphrasing concepts'),
    (4, 'Analytical Thinking', '분석적 사고', 'Comparison and classification', '비교와 분류', '이 두 개념의 차이점은...', 'Compare, contrast, categorize'),
    (5, 'Comprehensive Understanding', '종합적 이해', 'Integrating concepts', '개념 통합', '여러 요인들이 함께 작용하여...', 'Synthesis, cause-effect relationships'),
    (6, 'Evaluative Judgment', '평가적 판단', 'Critical thinking', '비판적 사고', '이 방법이 더 효과적인 이유는...', 'Evidence-based reasoning, critique'),
    (7, 'Creative Application', '창의적 적용', 'Novel solutions', '새로운 해결책', '새로운 상황에 적용하면...', 'Innovation, original thinking')
ON CONFLICT (level) DO NOTHING;

-- ================================================
-- Permissions (adjust based on your Railway setup)
-- ================================================

-- Grant permissions to application user (replace 'app_user' with actual user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;