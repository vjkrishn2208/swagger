import pinecone
from app_config import settings

def init_pinecone():
    pinecone.init(api_key=settings.PINECONE_API_KEY, environment="us-west1-gcp")

def create_index(index_name: str, dimension: int):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)

def get_index(index_name: str):
    return pinecone.Index(index_name)