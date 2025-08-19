-- Migration script to add teacher-specific fields to users table
-- Execute this after stopping the auth service

BEGIN;

-- Add teacher-specific columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS school VARCHAR(255),
ADD COLUMN IF NOT EXISTS subject VARCHAR(100),
ADD COLUMN IF NOT EXISTS grade_level VARCHAR(50),
ADD COLUMN IF NOT EXISTS role_description TEXT,
ADD COLUMN IF NOT EXISTS privacy_consent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS created_by_admin BOOLEAN DEFAULT FALSE;

-- Update existing users to have privacy_consent = TRUE (they already exist)
UPDATE users SET privacy_consent = TRUE WHERE privacy_consent IS NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_school ON users(school);
CREATE INDEX IF NOT EXISTS idx_users_subject ON users(subject);
CREATE INDEX IF NOT EXISTS idx_users_grade_level ON users(grade_level);

COMMIT;