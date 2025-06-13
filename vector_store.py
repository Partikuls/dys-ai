import openai
import pinecone
from pinecone import Pinecone
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import tiktoken

from config import config
from pdf_processor import DocumentChunk


class VectorStore:
    """
    Vector database interface for the Dyslexia RAG system.
    
    This class manages the vector database operations including embedding generation,
    document indexing, and semantic search. It uses OpenAI's embedding models for
    vector generation and Pinecone for scalable vector storage and retrieval.
    
    The vector store handles:
    - Embedding generation with automatic text truncation
    - Pinecone index creation and management
    - Batch document uploading with rate limiting
    - Semantic search with metadata filtering
    - Error handling for API failures
    
    Attributes:
        openai_client: OpenAI API client for generating embeddings
        pc: Pinecone client for vector database operations
        index: Active Pinecone index instance
        encoding: Tokenizer for text length management
    """
    def __init__(self) -> None:
        """
        Initialize the vector store with API clients.
        
        Sets up connections to OpenAI for embeddings and Pinecone for vector storage.
        The index connection is established separately via initialize_pinecone_index().
        
        Raises:
            openai.APIError: If OpenAI API key is invalid
            pinecone.exceptions.PineconeException: If Pinecone API key is invalid
        """
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index: Optional[pinecone.Index] = None
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
    def initialize_pinecone_index(self) -> None:
        """
        Initialize or connect to the Pinecone vector index.
        
        Creates a new index if it doesn't exist, or connects to an existing one.
        The index is configured with cosine similarity for educational content matching.
        
        Raises:
            pinecone.exceptions.PineconeException: If index creation or connection fails
            Exception: For other Pinecone API errors
            
        Note:
            Index creation is asynchronous and the method waits for readiness.
            Uses serverless configuration optimized for research document storage.
        """
        try:
            # Check if index exists
            if config.PINECONE_INDEX_NAME in [index.name for index in self.pc.list_indexes()]:
                print(f"Connecting to existing index: {config.PINECONE_INDEX_NAME}")
                self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
            else:
                print(f"Creating new index: {config.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=config.PINECONE_INDEX_NAME,
                    dimension=config.EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=pinecone.ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready before proceeding
                while not self.pc.describe_index(config.PINECONE_INDEX_NAME).status['ready']:
                    print("Waiting for index to be ready...")
                    time.sleep(1)
                
                self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
            
            print(f"Index stats: {self.index.describe_index_stats()}")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI's embedding model.
        
        Automatically handles text that exceeds token limits by truncating to
        the maximum safe length for the embedding model.
        
        Args:
            text: Input text to generate embedding for
        
        Returns:
            List[float]: Embedding vector of configured dimension
        
        Raises:
            openai.APIError: If embedding generation fails
            Exception: For token processing errors
        
        Note:
            Text is truncated to 8000 tokens to ensure compatibility with
            OpenAI embedding models and avoid API errors.
        """
        try:
            # Ensure text length is within embedding model limits
            tokens = self.encoding.encode(text)
            if len(tokens) > 8000:  # Conservative limit for embedding models
                # Truncate to safe length and decode back to text
                text = self.encoding.decode(tokens[:8000])
            
            response = self.openai_client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def batch_generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Génération des embeddings"):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.openai_client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Rate limiting - be nice to OpenAI
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in batch {i//batch_size}: {e}")
                # Fall back to individual embeddings for this batch
                for text in batch:
                    try:
                        embedding = self.generate_embedding(text)
                        embeddings.append(embedding)
                    except:
                        # Skip problematic texts
                        embeddings.append([0.0] * config.EMBEDDING_DIMENSION)
        
        return embeddings
    
    def upload_chunks_to_pinecone(self, chunks: List[DocumentChunk]):
        """Upload document chunks to Pinecone with embeddings"""
        if not self.index:
            self.initialize_pinecone_index()
        
        print(f"Traitement de {len(chunks)} segments pour téléchargement...")
        
        # Prepare texts for embedding
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = self.batch_generate_embeddings(texts)
        
        # Prepare vectors for upload
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector = {
                'id': chunk.chunk_id,
                'values': embedding,
                'metadata': {
                    'text': chunk.text,
                    'source': chunk.source,
                    'author': chunk.author,
                    'page_number': chunk.page_number,
                    'section': chunk.section,
                    'chunk_index': i
                }
            }
            vectors.append(vector)
        
        # Upload in batches to Pinecone
        batch_size = 100
        for i in tqdm(range(0, len(vectors), batch_size), desc="Téléchargement vers Pinecone"):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Erreur lors du téléchargement du lot {i//batch_size}: {e}")
        
        print(f"Téléchargement réussi de {len(vectors)} vecteurs vers Pinecone")
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.index:
            self.initialize_pinecone_index()
        
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results['matches']:
                result = {
                    'text': match['metadata']['text'],
                    'source': match['metadata']['source'],
                    'author': match['metadata']['author'],
                    'page_number': match['metadata']['page_number'],
                    'section': match['metadata']['section'],
                    'score': match['score']
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def delete_all_vectors(self):
        """Delete all vectors from the index (use with caution!)"""
        if not self.index:
            self.initialize_pinecone_index()
        
        try:
            self.index.delete(delete_all=True)
            print("All vectors deleted from index")
        except Exception as e:
            print(f"Error deleting vectors: {e}")
    
    def get_index_stats(self):
        """Get current index statistics"""
        if not self.index:
            self.initialize_pinecone_index()
        
        return self.index.describe_index_stats()

# Example usage
if __name__ == "__main__":
    # Test the vector store
    vs = VectorStore()
    vs.initialize_pinecone_index()
    
    # Test search (if index has data)
    results = vs.search("How to adapt teaching methods for dyslexic students?")
    if results:
        print("Search results:")
        for i, result in enumerate(results[:2]):
            print(f"\n{i+1}. Source: {result['source']} (Score: {result['score']:.3f})")
            print(f"   Author: {result['author']}")
            print(f"   Section: {result['section']}")
            print(f"   Text: {result['text'][:200]}...")
    else:
        print("No results found - index might be empty") 