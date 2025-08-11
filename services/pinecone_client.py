import pinecone
from app_config import settings
import logging
from typing import Optional, List, Dict, Any
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeClient:
    """Enhanced Pinecone client for CVP Lite knowledge base operations"""
    
    def __init__(self):
        self.index = None
        self.is_initialized = False
    
    def init_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            if not settings.PINECONE_API_KEY:
                logger.warning("Pinecone API key not configured")
                return False
            
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            # Check if index exists, create if not
            if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
                pinecone.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            # Get the index
            self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
            self.is_initialized = True
            
            logger.info("Pinecone initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            return False
    
    async def upsert_knowledge_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        namespace: str = "cvp_lite"
    ) -> bool:
        """Upsert knowledge vectors to Pinecone"""
        try:
            if not self.is_initialized or not self.index:
                logger.error("Pinecone not initialized")
                return False
            
            # Convert to Pinecone format
            pinecone_vectors = []
            for vector in vectors:
                pinecone_vectors.append({
                    "id": vector.get("id"),
                    "values": vector.get("values"),
                    "metadata": vector.get("metadata", {})
                })
            
            # Upsert vectors
            self.index.upsert(
                vectors=pinecone_vectors,
                namespace=namespace
            )
            
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vectors to Pinecone: {e}")
            return False
    
    async def search_knowledge(
        self, 
        query_vector: List[float], 
        top_k: int = 5,
        namespace: str = "cvp_lite",
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using vector similarity"""
        try:
            if not self.is_initialized or not self.index:
                logger.error("Pinecone not initialized")
                return []
            
            # Perform vector search
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Found {len(formatted_results)} relevant knowledge items")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    async def delete_knowledge_vectors(
        self, 
        vector_ids: List[str], 
        namespace: str = "cvp_lite"
    ) -> bool:
        """Delete knowledge vectors from Pinecone"""
        try:
            if not self.is_initialized or not self.index:
                logger.error("Pinecone not initialized")
                return False
            
            # Delete vectors
            self.index.delete(
                ids=vector_ids,
                namespace=namespace
            )
            
            logger.info(f"Deleted {len(vector_ids)} vectors from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {e}")
            return False
    
    async def get_index_stats(self) -> Optional[Dict[str, Any]]:
        """Get index statistics"""
        try:
            if not self.is_initialized or not self.index:
                logger.error("Pinecone not initialized")
                return None
            
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return None

# Global Pinecone client instance
pinecone_client = PineconeClient()

def init_pinecone():
    """Initialize Pinecone (legacy function for backward compatibility)"""
    return pinecone_client.init_pinecone()

def create_index(index_name: str, dimension: int):
    """Create Pinecone index (legacy function for backward compatibility)"""
    try:
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=dimension)
            logger.info(f"Created Pinecone index: {index_name}")
    except Exception as e:
        logger.error(f"Error creating index: {e}")

def get_index(index_name: str):
    """Get Pinecone index (legacy function for backward compatibility)"""
    try:
        return pinecone.Index(index_name)
    except Exception as e:
        logger.error(f"Error getting index: {e}")
        return None

# Async wrapper functions for backward compatibility
async def upsert_knowledge_vectors(vectors: List[Dict[str, Any]], namespace: str = "cvp_lite"):
    """Async wrapper for upserting knowledge vectors"""
    return await pinecone_client.upsert_knowledge_vectors(vectors, namespace)

async def search_knowledge(query_vector: List[float], top_k: int = 5, namespace: str = "cvp_lite", filter: Optional[Dict[str, Any]] = None):
    """Async wrapper for searching knowledge"""
    return await pinecone_client.search_knowledge(query_vector, top_k, namespace, filter)

async def delete_knowledge_vectors(vector_ids: List[str], namespace: str = "cvp_lite"):
    """Async wrapper for deleting knowledge vectors"""
    return await pinecone_client.delete_knowledge_vectors(vector_ids, namespace)

async def get_index_stats():
    """Async wrapper for getting index stats"""
    return await pinecone_client.get_index_stats()