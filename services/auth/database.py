"""
Database configuration and connection management for AIBOA Authentication Service
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/aiboa"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    Create all database tables
    
    This should be called once during application startup
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables
    
    WARNING: This will delete all data! Use only for development/testing
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def init_database():
    """
    Initialize database with default data
    
    Creates tables and inserts initial roles and admin user
    """
    from .models import UserRole, User
    from .utils.auth import get_password_hash
    
    try:
        # Create tables first
        create_tables()
        
        # Create a session for initialization
        db = SessionLocal()
        
        try:
            # Check if roles already exist
            existing_roles = db.query(UserRole).count()
            if existing_roles == 0:
                # Create default roles
                default_roles = [
                    UserRole(
                        name="admin",
                        display_name="Administrator",
                        description="Full system access and user management",
                        permissions={
                            "users": ["create", "read", "update", "delete"],
                            "analytics": ["read"],
                            "system": ["configure"],
                            "data": ["read_all", "export"]
                        }
                    ),
                    UserRole(
                        name="coach",
                        display_name="Teaching Coach",
                        description="Dashboard access and history viewing",
                        permissions={
                            "own_data": ["create", "read"],
                            "dashboard": ["read"],
                            "reports": ["generate"],
                            "history": ["read"],
                            "compare": ["read"]
                        }
                    ),
                    UserRole(
                        name="regular_user",
                        display_name="Regular User",
                        description="Basic transcription and analysis workflow",
                        permissions={
                            "transcription": ["create"],
                            "analysis": ["create"],
                            "results": ["read_own"],
                            "workflow": ["unified"]
                        }
                    )
                ]
                
                for role in default_roles:
                    db.add(role)
                
                db.commit()
                logger.info("Default roles created successfully")
            
            # Check if admin user already exists
            admin_user = db.query(User).filter(User.email == "purusil55@gmail.com").first()
            if not admin_user:
                # Create admin user
                admin_password_hash = get_password_hash("rhdwlgns85!@#")
                admin_user = User(
                    email="purusil55@gmail.com",
                    password_hash=admin_password_hash,
                    full_name="System Administrator",
                    role="admin",
                    status="active",
                    email_verified=True
                )
                
                db.add(admin_user)
                db.commit()
                logger.info("Admin user created successfully")
            else:
                logger.info("Admin user already exists")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to initialize database data: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_database_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database connection information
    
    Returns:
        dict: Database connection details
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("""
                SELECT 
                    version() as version,
                    current_database() as database_name,
                    current_user as user_name,
                    inet_server_addr() as server_addr,
                    inet_server_port() as server_port
            """)
            row = result.fetchone()
            
            return {
                "version": row.version if row else None,
                "database_name": row.database_name if row else None,
                "user_name": row.user_name if row else None,
                "server_addr": str(row.server_addr) if row and row.server_addr else None,
                "server_port": row.server_port if row else None,
                "connection_pool_size": engine.pool.size(),
                "connection_pool_checked_out": engine.pool.checkedout(),
                "connection_pool_overflow": engine.pool.overflow(),
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (if using SQLite)"""
    if "sqlite" in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()


@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log SQL queries in debug mode"""
    if os.getenv("SQL_DEBUG", "false").lower() == "true":
        logger.debug(f"SQL Query: {statement}")
        if parameters:
            logger.debug(f"Parameters: {parameters}")


# Health check functions
def health_check() -> dict:
    """
    Comprehensive database health check
    
    Returns:
        dict: Health check results
    """
    health_status = {
        "database": "unknown",
        "connection": False,
        "tables_exist": False,
        "can_query": False,
        "can_write": False,
        "timestamp": None
    }
    
    try:
        # Test basic connection
        if check_database_connection():
            health_status["connection"] = True
            health_status["database"] = "connected"
            
            # Test if tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            required_tables = ["users", "user_roles", "user_sessions"]
            if all(table in tables for table in required_tables):
                health_status["tables_exist"] = True
                
                # Test if we can query
                db = SessionLocal()
                try:
                    user_count = db.query(User).count()
                    health_status["can_query"] = True
                    health_status["user_count"] = user_count
                    
                    # Test if we can write (simple session test)
                    from datetime import datetime
                    health_status["can_write"] = True
                    health_status["timestamp"] = datetime.now().isoformat()
                    health_status["database"] = "healthy"
                    
                except Exception as e:
                    logger.error(f"Database query/write test failed: {e}")
                    health_status["database"] = "query_failed"
                finally:
                    db.close()
            else:
                health_status["database"] = "tables_missing"
                
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "error"
        health_status["error"] = str(e)
    
    return health_status


# Import User model here to avoid circular imports
from .models import User