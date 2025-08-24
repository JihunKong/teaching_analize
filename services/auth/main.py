#!/usr/bin/env python3
"""
AIBOA Auth Service
Simple authentication service for teachers
"""

import os
import hashlib
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIBOA Auth Service",
    description="Authentication service for educational platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'aiboa-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

security = HTTPBearer()

# Initialize SQLite database
def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            school TEXT,
            subject TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    school: Optional[str] = None
    subject: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: int
    email: str
    name: str
    school: Optional[str]
    subject: Optional[str]
    created_at: str

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, email, password_hash, name, school, subject, created_at FROM users WHERE email = ?",
        (email,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "password_hash": row[2],
            "name": row[3],
            "school": row[4],
            "subject": row[5],
            "created_at": row[6]
        }
    return None

def create_user(user_data: UserCreate) -> Dict[str, Any]:
    """Create new user in database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(user_data.password)
        
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, name, school, subject)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_data.email, password_hash, user_data.name, user_data.school, user_data.subject)
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "school": user_data.school,
            "subject": user_data.subject,
            "created_at": datetime.now().isoformat()
        }
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    finally:
        conn.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth", "timestamp": datetime.now().isoformat()}

@app.post("/api/register")
async def register(user_data: UserCreate):
    """Register new user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        new_user = create_user(user_data)
        
        # Create access token
        token_data = {
            "user_id": new_user["id"],
            "email": new_user["email"],
            "name": new_user["name"]
        }
        access_token = create_access_token(token_data)
        
        return {
            "message": "User created successfully",
            "user": UserProfile(**new_user),
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/login")
async def login(login_data: UserLogin):
    """Login user"""
    try:
        # Get user from database
        user = get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        conn.close()
        
        # Create access token
        token_data = {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
        access_token = create_access_token(token_data)
        
        return {
            "message": "Login successful",
            "user": UserProfile(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                school=user["school"],
                subject=user["subject"],
                created_at=user["created_at"]
            ),
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/profile")
async def get_profile(token_data: Dict[str, Any] = Depends(verify_token)):
    """Get user profile"""
    try:
        user = get_user_by_email(token_data["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            school=user["school"],
            subject=user["subject"],
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve profile")

@app.get("/api/verify")
async def verify_token_endpoint(token_data: Dict[str, Any] = Depends(verify_token)):
    """Verify token validity"""
    return {"valid": True, "user_id": token_data["user_id"], "email": token_data["email"]}

@app.get("/api/stats")
async def get_stats():
    """Get auth service statistics"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL")
        active_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "service": "auth",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return {"error": "Could not retrieve stats"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)