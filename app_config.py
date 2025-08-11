import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_TITLE: str = "CVP Lite - AI Mentor Backend"
    API_DESCRIPTION: str = "Complete Career Vision Program Lite with AI-powered assessments and guidance"
    API_VERSION: str = "1.0.0"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "cvp-lite-knowledge")
    
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb+srv://pingmedia:kmBSuNAGq1aclhFU@ypd-cluster.6dddffx.mongodb.net/?retryWrites=true&w=majority&appName=YPD-Cluster")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "cvp_lite_db")
    
    # CVP Lite Configuration
    MAX_STEPS: int = 10
    SUPPORTED_LANGUAGES: list = ["en", "es", "fr", "de", "zh", "ja"]
    SUPPORTED_TIERS: list = ["basic", "premium", "enterprise"]
    
    # Scoring Configuration
    MIN_SCORE: int = 0
    MAX_SCORE: int = 100
    PASSING_SCORE: int = 70

settings = Settings()