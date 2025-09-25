# backend/database/connection.py

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import db_config
from ..models.resume import Resume
from ..models.job_description import JobDescription
from ..models.match_result import MatchResult
from ..models.audit_log import AuditLog

# Global MongoDB client
mongodb_client = None

async def connect_to_mongo():
    """Create database connection"""
    global mongodb_client
    try:
        print(f"🔄 Connecting to MongoDB: {db_config.get_mongodb_url()[:50]}...")
        mongodb_client = AsyncIOMotorClient(
            db_config.get_mongodb_url(),
            maxPoolSize=db_config.max_connections,
            minPoolSize=db_config.min_connections,
            serverSelectionTimeoutMS=db_config.server_selection_timeout_ms,
            connectTimeoutMS=db_config.connect_timeout_ms,
            socketTimeoutMS=db_config.socket_timeout_ms,
            retryWrites=db_config.retry_writes
        )
        
        # Test the connection
        await mongodb_client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        raise e
    
    # Initialize Beanie with the database and models
    try:
        print(f"🔄 Initializing Beanie with database: {db_config.get_database_name()}")
        await init_beanie(
            database=mongodb_client[db_config.get_database_name()],
            document_models=[
                Resume,
                JobDescription, 
                MatchResult,
                AuditLog
            ]
        )
        print("✅ Beanie initialization successful!")
    except Exception as e:
        print(f"❌ Beanie initialization failed: {str(e)}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()

def get_database():
    """Get the MongoDB database instance"""
    return mongodb_client[db_config.get_database_name()]

# For backward compatibility with dependency injection
async def get_db():
    """Dependency to get database - for MongoDB this just returns None since Beanie handles connections"""
    # With Beanie, we don't need to inject database sessions like SQLAlchemy
    # Models handle their own database operations
    return None

# Initialization function for FastAPI startup
async def init_database():
    """Initialize database connection and models"""
    await connect_to_mongo()
    print(f"Connected to MongoDB database: {db_config.get_database_name()}")

# Cleanup function for FastAPI shutdown  
async def close_database():
    """Close database connections"""
    await close_mongo_connection()
    print("Disconnected from MongoDB")