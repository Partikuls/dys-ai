import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Configuration class for the Dyslexia RAG System.
    
    This class manages all configuration parameters for the dyslexia education
    RAG system, including API credentials, model settings, document processing
    parameters, and vector database configuration.
    
    The configuration supports multiple ways to provide API keys:
    - Environment variables (recommended for production)
    - Direct file reading (pinecone.api.txt)
    - Default placeholder values (for development setup)
    
    Attributes:
        OPENAI_API_KEY: OpenAI API key for embeddings and chat completions
        PINECONE_API_KEY: Pinecone API key for vector database operations
        PINECONE_INDEX_NAME: Name of the Pinecone index for storing embeddings
        PINECONE_ENVIRONMENT: Pinecone environment (e.g., 'gcp-starter')
        EMBEDDING_DIMENSION: Dimension of the embedding vectors (1536 for text-embedding-3-small)
        EMBEDDING_MODEL: OpenAI model used for generating embeddings
        CHAT_MODEL: OpenAI model used for chat completions
        PDF_DIRECTORY: Directory containing academic research PDFs
        CHUNK_SIZE: Maximum size of text chunks in tokens
        CHUNK_OVERLAP: Overlap between consecutive chunks in tokens
        TOP_K_RESULTS: Number of most relevant chunks to retrieve for each query
        MAX_CONTEXT_LENGTH: Maximum context length for chat completions
    """
    # API Keys - Set via environment variables or direct file reading
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Pinecone API key - Read from file first, fallback to environment variable
    PINECONE_API_KEY: Optional[str] = None
    try:
        # Primary method: Read from pinecone.api.txt file
        with open("pinecone.api.txt", "r", encoding="utf-8") as f:
            PINECONE_API_KEY = f.read().strip()
    except FileNotFoundError:
        # Fallback: Use environment variable or placeholder
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key-here")
    
    # Pinecone Vector Database Configuration
    PINECONE_INDEX_NAME: str = "dyslexia-research"  # Index name for storing research embeddings
    PINECONE_ENVIRONMENT: str = "gcp-starter"  # Pinecone environment (update for your setup)
    # Embedding dimensions must match the chosen OpenAI embedding model:
    # - text-embedding-3-small: 1536 dimensions
    # - text-embedding-3-large: 3072 dimensions
    EMBEDDING_DIMENSION: int = 1536
    
    # OpenAI Model Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # Model for generating text embeddings
    CHAT_MODEL: str = "gpt-4o"  # Model for generating educational recommendations
    
    # Document Processing Configuration
    PDF_DIRECTORY: str = "pdf"  # Directory containing academic research PDFs
    CHUNK_SIZE: int = 1000  # Maximum tokens per text chunk for embeddings
    CHUNK_OVERLAP: int = 200  # Token overlap between consecutive chunks (maintains context)
    
    # RAG (Retrieval-Augmented Generation) Configuration
    TOP_K_RESULTS: int = 5  # Number of most relevant chunks to retrieve per query
    MAX_CONTEXT_LENGTH: int = 4000  # Maximum context length for chat completions (tokens)

# Global configuration instance - import this in other modules
config: Config = Config() 