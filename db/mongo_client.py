from motor.motor_asyncio import AsyncIOMotorClient
from app_config import settings
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for database connection
client: Optional[AsyncIOMotorClient] = None
database = None
sessions_collection = None
assessments_collection = None
career_domains_collection = None
learning_pathways_collection = None

async def connect_to_mongo():
    """Connect to MongoDB database"""
    global client, database, sessions_collection, assessments_collection, career_domains_collection, learning_pathways_collection
    
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get database and collections
        database = client[settings.MONGO_DB_NAME]
        sessions_collection = database.get_collection("sessions")
        assessments_collection = database.get_collection("assessments")
        career_domains_collection = database.get_collection("career_domains")
        learning_pathways_collection = database.get_collection("learning_pathways")
        
        # Create indexes for better performance
        await _create_indexes()
        
        logger.info(f"Connected to database: {settings.MONGO_DB_NAME}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def _create_indexes():
    """Create database indexes for better performance"""
    try:
        # Sessions collection indexes
        await sessions_collection.create_index("session_id", unique=True)
        await sessions_collection.create_index("student_id")
        await sessions_collection.create_index("created_at")
        
        # Assessments collection indexes
        await assessments_collection.create_index("session_id")
        await assessments_collection.create_index("step_type")
        
        # Career domains collection indexes
        await career_domains_collection.create_index("domain_id", unique=True)
        
        # Learning pathways collection indexes
        await learning_pathways_collection.create_index("pathway_id", unique=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create some indexes: {e}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        try:
            client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

async def get_session(session_id: str):
    """Get a session by ID"""
    try:
        if not sessions_collection:
            raise Exception("Database not connected")
        
        session = await sessions_collection.find_one({"session_id": session_id})
        return session
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise

async def save_session(session_data: dict):
    """Save or update a session"""
    try:
        if not sessions_collection:
            raise Exception("Database not connected")
        
        # Use upsert to create or update
        result = await sessions_collection.update_one(
            {"session_id": session_data["session_id"]},
            {"$set": session_data},
            upsert=True
        )
        return result
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        raise

async def save_assessment(assessment_data: dict):
    """Save an assessment result"""
    try:
        if not assessments_collection:
            raise Exception("Database not connected")
        
        result = await assessments_collection.insert_one(assessment_data)
        return result
    except Exception as e:
        logger.error(f"Error saving assessment: {e}")
        raise

async def get_assessments(session_id: str):
    """Get all assessments for a session"""
    try:
        if not assessments_collection:
            raise Exception("Database not connected")
        
        cursor = assessments_collection.find({"session_id": session_id})
        assessments = await cursor.to_list(length=None)
        return assessments
    except Exception as e:
        logger.error(f"Error getting assessments for session {session_id}: {e}")
        raise

async def save_career_domains(domains: list):
    """Save career domains to database"""
    try:
        if not career_domains_collection:
            raise Exception("Database not connected")
        
        # Clear existing domains and insert new ones
        await career_domains_collection.delete_many({})
        
        if domains:
            result = await career_domains_collection.insert_many(domains)
            logger.info(f"Saved {len(result.inserted_ids)} career domains")
            return result
    except Exception as e:
        logger.error(f"Error saving career domains: {e}")
        raise

async def get_career_domains():
    """Get all career domains from database"""
    try:
        if not career_domains_collection:
            raise Exception("Database not connected")
        
        cursor = career_domains_collection.find({})
        domains = await cursor.to_list(length=None)
        return domains
    except Exception as e:
        logger.error(f"Error getting career domains: {e}")
        raise

async def save_learning_pathways(pathways: list):
    """Save learning pathways to database"""
    try:
        if not learning_pathways_collection:
            raise Exception("Database not connected")
        
        # Clear existing pathways and insert new ones
        await learning_pathways_collection.delete_many({})
        
        if pathways:
            result = await learning_pathways_collection.insert_many(pathways)
            logger.info(f"Saved {len(result.inserted_ids)} learning pathways")
            return result
    except Exception as e:
        logger.error(f"Error saving learning pathways: {e}")
        raise

async def get_learning_pathways():
    """Get all learning pathways from database"""
    try:
        if not learning_pathways_collection:
            raise Exception("Database not connected")
        
        cursor = learning_pathways_collection.find({})
        pathways = await cursor.to_list(length=None)
        return pathways
    except Exception as e:
        logger.error(f"Error getting learning pathways: {e}")
        raise

async def get_session_progress(session_id: str):
    """Get session progress summary"""
    try:
        if not sessions_collection or not assessments_collection:
            raise Exception("Database not connected")
        
        # Get session
        session = await get_session(session_id)
        if not session:
            return None
        
        # Get assessments count
        assessments_count = await assessments_collection.count_documents({"session_id": session_id})
        
        # Calculate progress
        progress = {
            "session_id": session_id,
            "total_steps": 10,  # CVP Lite has 10 steps
            "completed_steps": assessments_count,
            "completion_percentage": (assessments_count / 10) * 100,
            "current_step": session.get("current_step", 0),
            "last_updated": session.get("last_updated")
        }
        
        return progress
    except Exception as e:
        logger.error(f"Error getting session progress for {session_id}: {e}")
        raise

async def search_sessions(query: dict, limit: int = 50):
    """Search sessions based on criteria"""
    try:
        if not sessions_collection:
            raise Exception("Database not connected")
        
        cursor = sessions_collection.find(query).limit(limit)
        sessions = await cursor.to_list(length=limit)
        return sessions
    except Exception as e:
        logger.error(f"Error searching sessions: {e}")
        raise

async def delete_session(session_id: str):
    """Delete a session and all related data"""
    try:
        if not sessions_collection or not assessments_collection:
            raise Exception("Database not connected")
        
        # Delete session
        session_result = await sessions_collection.delete_one({"session_id": session_id})
        
        # Delete related assessments
        assessments_result = await assessments_collection.delete_many({"session_id": session_id})
        
        logger.info(f"Deleted session {session_id} and {assessments_result.deleted_count} assessments")
        return session_result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise

async def get_database_stats():
    """Get database statistics"""
    try:
        if not database:
            raise Exception("Database not connected")
        
        stats = {
            "sessions_count": await sessions_collection.count_documents({}),
            "assessments_count": await assessments_collection.count_documents({}),
            "career_domains_count": await career_domains_collection.count_documents({}),
            "learning_pathways_count": await learning_pathways_collection.count_documents({})
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise