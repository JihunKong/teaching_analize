#!/usr/bin/env python3
"""
Script to create test users in the AIBOA database
"""

import sys
import os
import hashlib
from datetime import datetime

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor

def hash_password(password: str) -> str:
    """Simple password hashing using bcrypt-like method"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_test_users():
    """Create test users in the database"""
    
    # Database connection
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="aiboa", 
            user="postgres",
            password="password"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test users to create
        test_users = [
            {
                "email": "teacher1@test.com",
                "password": "teacher123!",
                "full_name": "김영희 선생님",
                "role": "regular_user",
                "school": "서울초등학교",
                "subject": "수학",
                "grade_level": "3학년",
                "role_description": "3학년 담임 및 수학 전담"
            },
            {
                "email": "teacher2@test.com",
                "password": "teacher123!",
                "full_name": "이민수 선생님", 
                "role": "regular_user",
                "school": "부산중학교",
                "subject": "영어",
                "grade_level": "1학년",
                "role_description": "1학년 영어 전담"
            },
            {
                "email": "teacher3@test.com",
                "password": "teacher123!",
                "full_name": "박지은 선생님",
                "role": "regular_user", 
                "school": "대구고등학교",
                "subject": "과학",
                "grade_level": "2학년",
                "role_description": "2학년 물리 담당"
            },
            {
                "email": "coach1@test.com",
                "password": "coach123!",
                "full_name": "최수진 코치",
                "role": "coach",
                "school": "교육청",
                "subject": "교육지도",
                "grade_level": "전체",
                "role_description": "수업 컨설팅 및 코칭"
            },
            {
                "email": "coach2@test.com", 
                "password": "coach123!",
                "full_name": "김동현 코치",
                "role": "coach",
                "school": "교육청",
                "subject": "수업분석",
                "grade_level": "전체", 
                "role_description": "AI 기반 수업 분석 전문가"
            },
            {
                "email": "coach3@test.com",
                "password": "coach123!",
                "full_name": "이혜진 코치",
                "role": "coach",
                "school": "교육연구원",
                "subject": "교육과정",
                "grade_level": "전체",
                "role_description": "교육과정 및 평가 전문가"
            }
        ]
        
        # Create each user
        for user_data in test_users:
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email = %s", (user_data["email"],))
            if cur.fetchone():
                print(f"User {user_data['email']} already exists, skipping...")
                continue
            
            # Hash password
            password_hash = hash_password(user_data["password"])
            
            # Insert user
            insert_query = """
                INSERT INTO users (
                    email, password_hash, full_name, role, status, 
                    email_verified, school, subject, grade_level, 
                    role_description, privacy_consent, created_by_admin,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, 'active',
                    true, %s, %s, %s,
                    %s, true, true,
                    %s, %s
                )
            """
            
            now = datetime.utcnow()
            cur.execute(insert_query, (
                user_data["email"],
                password_hash,
                user_data["full_name"],
                user_data["role"], 
                user_data["school"],
                user_data["subject"],
                user_data["grade_level"],
                user_data["role_description"],
                now,
                now
            ))
            
            print(f"Created user: {user_data['email']} ({user_data['full_name']})")
        
        # Commit changes
        conn.commit()
        print("\nAll test users created successfully!")
        
    except Exception as e:
        print(f"Error creating test users: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    create_test_users()