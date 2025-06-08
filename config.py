import os
from pathlib import Path

# Configuration for the Dyslexia RAG System
class Config:
    # API Keys - you'll need to set these as environment variables or update directly
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Read Pinecone API key from the existing file
    PINECONE_API_KEY = None
    try:
        with open("pinecone.api.txt", "r") as f:
            PINECONE_API_KEY = f.read().strip()
    except FileNotFoundError:
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key-here")
    
    # Pinecone Configuration
    PINECONE_INDEX_NAME = "dyslexia-research"
    PINECONE_ENVIRONMENT = "gcp-starter"  # Update based on your Pinecone environment
    EMBEDDING_DIMENSION = 1536  # text-embedding-3-small: 1536, text-embedding-3-large: 3072
    
    # OpenAI Configuration
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o"
    
    # Document Processing
    PDF_DIRECTORY = "pdf"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # RAG Configuration
    TOP_K_RESULTS = 5
    MAX_CONTEXT_LENGTH = 4000

# Create config instance
config = Config() 