-- AIBOA Database Migration Script
-- Migrates existing data to new user role-based schema

-- ============================================
-- Pre-migration backup commands (run manually)
-- ============================================
-- pg_dump -h localhost -U postgres -d aiboa > backup_before_migration.sql
-- pg_dump -h localhost -U postgres -d aiboa --schema-only > schema_backup.sql

-- ============================================
-- Step 1: Create backup of existing data
-- ============================================

-- Backup existing transcription_jobs if table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'transcription_jobs') THEN
        CREATE TABLE transcription_jobs_backup AS SELECT * FROM transcription_jobs;
        RAISE NOTICE 'Backed up existing transcription_jobs table';
    END IF;
END $$;

-- Backup existing analysis_results if table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis_results') THEN
        CREATE TABLE analysis_results_backup AS SELECT * FROM analysis_results;
        RAISE NOTICE 'Backed up existing analysis_results table';
    END IF;
END $$;

-- ============================================
-- Step 2: Drop existing tables to recreate with new schema
-- ============================================

DROP TABLE IF EXISTS analysis_results CASCADE;
DROP TABLE IF EXISTS transcription_jobs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- Step 3: Apply new schema
-- ============================================

-- This will run the schema.sql file content
-- (In practice, you would run: \i /path/to/schema.sql)

-- ============================================
-- Step 4: Create initial admin user
-- ============================================

-- Create the initial admin user with hashed password
-- Password: rhdwlgns85!@# (will be hashed by the application)
INSERT INTO users (
    email, 
    password_hash, 
    full_name, 
    role, 
    status, 
    email_verified,
    created_at
) VALUES (
    'purusil55@gmail.com',
    '$2b$12$placeholder_hash_will_be_replaced_by_auth_service',
    'System Administrator',
    'admin',
    'active',
    true,
    CURRENT_TIMESTAMP
);

-- ============================================
-- Step 5: Migrate existing data if backups exist
-- ============================================

-- Migrate transcription jobs (assign to admin user initially)
DO $$ 
DECLARE
    admin_user_id INTEGER;
BEGIN
    -- Get admin user ID
    SELECT id INTO admin_user_id FROM users WHERE email = 'purusil55@gmail.com';
    
    -- Migrate transcription jobs if backup exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'transcription_jobs_backup') THEN
        INSERT INTO transcription_jobs (
            job_id,
            user_id,
            status,
            progress,
            source_type,
            source_url,
            filename,
            language,
            export_format,
            transcript_text,
            metadata,
            error_message,
            created_at,
            started_at,
            completed_at
        )
        SELECT 
            COALESCE(job_id, 'migrated_' || id::text),
            admin_user_id, -- Assign all old data to admin initially
            COALESCE(status, 'completed'),
            COALESCE(progress, 100),
            CASE 
                WHEN source_url IS NOT NULL AND source_url LIKE '%youtube%' THEN 'youtube'
                ELSE 'upload'
            END,
            source_url,
            filename,
            COALESCE(language, 'ko'),
            COALESCE(export_format, 'json'),
            transcript_text,
            COALESCE(metadata, '{}')::jsonb,
            error_message,
            COALESCE(created_at, CURRENT_TIMESTAMP),
            started_at,
            completed_at
        FROM transcription_jobs_backup;
        
        RAISE NOTICE 'Migrated % transcription jobs', (SELECT COUNT(*) FROM transcription_jobs_backup);
    END IF;

    -- Migrate analysis results if backup exists  
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis_results_backup') THEN
        INSERT INTO analysis_results (
            user_id,
            transcription_job_id,
            analysis_type,
            framework,
            input_text,
            results,
            overall_score,
            primary_level,
            processing_time_seconds,
            word_count,
            sentence_count,
            created_at
        )
        SELECT 
            admin_user_id, -- Assign all old data to admin initially
            NULL, -- Will need manual linking if needed
            COALESCE(analysis_type, 'comprehensive'),
            COALESCE(framework, 'cbil'),
            COALESCE(input_text, ''),
            COALESCE(results, '{}')::jsonb,
            overall_score,
            primary_level,
            processing_time_seconds,
            word_count,
            sentence_count,
            COALESCE(created_at, CURRENT_TIMESTAMP)
        FROM analysis_results_backup;
        
        RAISE NOTICE 'Migrated % analysis results', (SELECT COUNT(*) FROM analysis_results_backup);
    END IF;
END $$;

-- ============================================
-- Step 6: Create sample data for testing
-- ============================================

-- Create a sample coach user for testing
INSERT INTO users (
    email, 
    password_hash, 
    full_name, 
    role, 
    status, 
    email_verified,
    created_by,
    created_at
) VALUES (
    'coach.test@example.com',
    '$2b$12$placeholder_hash_for_testing',
    'Test Coach User',
    'coach',
    'active',
    true,
    (SELECT id FROM users WHERE email = 'purusil55@gmail.com'),
    CURRENT_TIMESTAMP
);

-- Create a sample regular user for testing  
INSERT INTO users (
    email, 
    password_hash, 
    full_name, 
    role, 
    status, 
    email_verified,
    created_by,
    created_at
) VALUES (
    'user.test@example.com',
    '$2b$12$placeholder_hash_for_testing',
    'Test Regular User',
    'regular_user',
    'active',
    true,
    (SELECT id FROM users WHERE email = 'purusil55@gmail.com'),
    CURRENT_TIMESTAMP
);

-- ============================================
-- Step 7: Update system statistics
-- ============================================

-- Generate initial usage statistics
INSERT INTO usage_statistics (
    user_id,
    metric_name,
    metric_value,
    aggregation_period,
    period_start,
    period_end,
    created_at
)
SELECT 
    u.id,
    'total_transcriptions',
    COUNT(tj.id),
    'monthly',
    DATE_TRUNC('month', CURRENT_DATE),
    DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day',
    CURRENT_TIMESTAMP
FROM users u
LEFT JOIN transcription_jobs tj ON u.id = tj.user_id
GROUP BY u.id;

INSERT INTO usage_statistics (
    user_id,
    metric_name,
    metric_value,
    aggregation_period,
    period_start,
    period_end,
    created_at
)
SELECT 
    u.id,
    'total_analyses',
    COUNT(ar.id),
    'monthly',
    DATE_TRUNC('month', CURRENT_DATE),
    DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day',
    CURRENT_TIMESTAMP
FROM users u
LEFT JOIN analysis_results ar ON u.id = ar.user_id
GROUP BY u.id;

-- ============================================
-- Step 8: Verification queries
-- ============================================

-- Verify migration success
DO $$
DECLARE
    user_count INTEGER;
    transcription_count INTEGER;
    analysis_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO transcription_count FROM transcription_jobs;
    SELECT COUNT(*) INTO analysis_count FROM analysis_results;
    
    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE '- Users: %', user_count;
    RAISE NOTICE '- Transcription Jobs: %', transcription_count;
    RAISE NOTICE '- Analysis Results: %', analysis_count;
    
    -- Verify admin user exists
    IF EXISTS (SELECT 1 FROM users WHERE email = 'purusil55@gmail.com' AND role = 'admin') THEN
        RAISE NOTICE '- Admin user created successfully';
    ELSE
        RAISE WARNING 'Admin user creation failed!';
    END IF;
END $$;

-- ============================================
-- Step 9: Clean up backup tables (optional)
-- ============================================

-- Uncomment these lines after verifying migration success
-- DROP TABLE IF EXISTS transcription_jobs_backup;
-- DROP TABLE IF EXISTS analysis_results_backup;

-- ============================================
-- Step 10: Grant permissions for application users
-- ============================================

-- Create application database users (run these manually with appropriate passwords)
-- CREATE USER aiboa_app WITH PASSWORD 'secure_app_password';
-- CREATE USER aiboa_readonly WITH PASSWORD 'secure_readonly_password';

-- Grant permissions to application user
-- GRANT CONNECT ON DATABASE aiboa TO aiboa_app;
-- GRANT USAGE ON SCHEMA public TO aiboa_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO aiboa_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aiboa_app;

-- Grant read-only permissions for monitoring
-- GRANT CONNECT ON DATABASE aiboa TO aiboa_readonly;
-- GRANT USAGE ON SCHEMA public TO aiboa_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO aiboa_readonly;

-- ============================================
-- Migration completion log
-- ============================================

INSERT INTO user_activity_logs (
    user_id,
    action,
    resource_type,
    details,
    created_at
) VALUES (
    (SELECT id FROM users WHERE email = 'purusil55@gmail.com'),
    'DATABASE_MIGRATION',
    'system',
    '{"migration_version": "1.0.0", "status": "completed", "timestamp": "' || CURRENT_TIMESTAMP || '"}',
    CURRENT_TIMESTAMP
);

RAISE NOTICE 'Database migration completed successfully. Schema version 1.0.0 applied.';