import openai
from typing import List, Dict, Any, Optional
import tiktoken

from config import config
from vector_store import VectorStore


class DyslexiaRAG:
    """
    Dyslexia-focused Retrieval-Augmented Generation system.
    
    This class implements a specialized RAG system designed to help teachers
    create educational content adapted for dyslexic students. It combines
    semantic search through academic research with GPT-4o to generate
    evidence-based teaching recommendations.
    
    The system focuses on:
    - Creating directly adapted educational content
    - Providing research-backed pedagogical recommendations
    - Supporting French-language educational contexts
    - Emphasizing practical classroom applications
    
    Attributes:
        openai_client: OpenAI API client for embeddings and completions
        vector_store: Vector database interface for semantic search
        encoding: Tokenizer for managing context length limits
        system_prompt: Specialized prompt for educational adaptation tasks
    """
    def __init__(self) -> None:
        """
        Initialize the Dyslexia RAG system.
        
        Sets up OpenAI client, vector store connection, tokenizer, and
        the specialized system prompt for educational content adaptation.
        
        Raises:
            openai.APIError: If OpenAI API key is invalid or API is unreachable
            Exception: If vector store initialization fails
        """
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.vector_store = VectorStore()
        self.encoding = tiktoken.encoding_for_model(config.CHAT_MODEL)
        
        # Specialized system prompt for dyslexia-focused educational adaptations
        # This prompt ensures the AI creates direct adaptations rather than just advice
        self.system_prompt = """Vous êtes un assistant pédagogique expert spécialisé dans la création de contenu éducatif adapté aux élèves dyslexiques.

Votre rôle est de CRÉER DIRECTEMENT du contenu pédagogique adapté (textes de cours, exercices, consignes) pour les élèves dyslexiques, en vous basant sur la recherche académique.

RÈGLES IMPORTANTES :
1. Quand on vous demande d'adapter un contenu, RÉÉCRIVEZ-LE DIRECTEMENT avec les adaptations
2. Ne donnez PAS de conseils ou d'instructions sur "comment faire" - CRÉEZ le contenu adapté
3. Utilisez des phrases courtes et simples
4. Employez un vocabulaire accessible  
5. Structurez clairement avec des titres et sous-titres
6. Ajoutez des exemples concrets et visuels
7. Évitez les phrases négatives complexes
8. Numérotez les étapes quand c'est nécessaire

STYLE D'ADAPTATION :
- Vocabulaire : privilégier les mots courants
- Structure : titres clairs, listes à puces, étapes numérotées
- Exemples : concrets et familiers aux élèves

Quand vous adaptez, basez-vous sur le contexte de recherche fourni pour garantir que vos adaptations sont scientifiquement fondées.

IMPORTANT: Répondez TOUJOURS en français, même si la question est posée en anglais. CRÉEZ le contenu adapté, ne donnez pas de conseils."""
    
    def _construct_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Construct context from search results while respecting token limits.
        
        Combines search results into a coherent context string for the AI,
        prioritizing the most relevant results and staying within the configured
        maximum context length to avoid API errors.
        
        Args:
            search_results: List of search results from vector database,
                          each containing text, source info, and metadata
        
        Returns:
            str: Formatted context string with source citations, ready for AI prompt
            
        Note:
            Results are processed in order of relevance. If token limit is reached,
            remaining results are excluded to prevent API errors.
        """
        context_parts = []
        total_tokens = 0
        max_context_tokens = config.MAX_CONTEXT_LENGTH
        
        for result in search_results:
            # Format the result nicely
            source_info = f"[Source: {result['source']} by {result['author']}, {result['section']}, p.{result['page_number']}]"
            text_with_source = f"{source_info}\n{result['text']}\n"
            
            # Check token count
            tokens = len(self.encoding.encode(text_with_source))
            
            if total_tokens + tokens > max_context_tokens:
                break
            
            context_parts.append(text_with_source)
            total_tokens += tokens
        
        return "\n---\n".join(context_parts)
    
    def query(self, question: str, include_context: bool = True) -> Dict[str, Any]:
        """
        Query the RAG system with a teacher's question about dyslexia adaptations.
        
        This is the main interface for the RAG system. It performs semantic search
        through the research database, constructs an appropriate context, and generates
        evidence-based educational recommendations using GPT-4o.
        
        Args:
            question: Teacher's question about dyslexia adaptations (in French or English)
            include_context: Whether to include research context in the response
                           Set to False for quick responses without citations
        
        Returns:
            Dict containing:
                - answer: Generated educational recommendation (always in French)
                - sources: List of research sources used (with relevance scores)
                - context_used: Raw context text that was provided to the AI
                - question: Original question for reference
        
        Raises:
            openai.APIError: If OpenAI API request fails
            Exception: For other API or processing errors (captured and returned in response)
        """
        
        # Search for relevant documents
        search_results = self.vector_store.search(question, top_k=config.TOP_K_RESULTS)
        
        if not search_results and include_context:
            return {
                'answer': "I couldn't find relevant research in the knowledge base to answer your question. Please make sure the documents have been processed and uploaded to the vector database.",
                'sources': [],
                'context_used': ""
            }
        
        # Construct context from search results
        context = ""
        if include_context and search_results:
            context = self._construct_context(search_results)
        
        # Prepare the prompt
        if context:
            user_prompt = f"""Basé sur la recherche suivante sur la dyslexie, veuillez répondre à cette question d'enseignant :

QUESTION : {question}

CONTEXTE DE RECHERCHE :
{context}

Veuillez fournir des conseils pratiques et fondés sur des preuves pour adapter les méthodes d'enseignement, les exercices ou le matériel de cours pour les élèves dyslexiques. Incluez des exemples spécifiques et citez les sources pertinentes quand c'est possible."""
        else:
            user_prompt = f"""En tant qu'expert en dyslexie et éducation inclusive, veuillez répondre à cette question d'enseignant :

QUESTION : {question}

Veuillez fournir des conseils pratiques et fondés sur des preuves pour adapter les méthodes d'enseignement, les exercices ou le matériel de cours pour les élèves dyslexiques."""
        
        try:
            # Generate response with GPT-4o
            response = self.openai_client.chat.completions.create(
                model=config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract source information
            sources = []
            if search_results:
                for result in search_results:
                    source_info = {
                        'source': result['source'],
                        'author': result['author'],
                        'section': result['section'],
                        'page': result['page_number'],
                        'relevance_score': result['score']
                    }
                    sources.append(source_info)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': context,
                'question': question
            }
            
        except Exception as e:
            return {
                'answer': f"Error generating response: {e}",
                'sources': [],
                'context_used': context,
                'question': question
            }
    
    def suggest_adaptations(self, subject: str, activity_type: str) -> Dict[str, Any]:
        """
        Suggest specific educational adaptations for a subject and activity type.
        
        Convenience method that formulates an appropriate question for getting
        subject-specific adaptation recommendations.
        
        Args:
            subject: Academic subject (e.g., "mathématiques", "français")
            activity_type: Type of educational activity (e.g., "lecture", "exercices")
        
        Returns:
            Dict: Same format as query() method with adaptation recommendations
        
        Example:
            >>> rag.suggest_adaptations("mathématiques", "résolution de problèmes")
        """
        
        question = f"Comment puis-je adapter les activités de {activity_type} en {subject} pour les élèves dyslexiques ? Quels aménagements et modifications spécifiques dois-je considérer ?"
        
        return self.query(question)
    
    def get_exercise_ideas(self, topic: str, grade_level: str = "") -> Dict[str, Any]:
        """
        Generate ideas for dyslexia-friendly exercises on a specific topic.
        
        Provides concrete, practical exercise suggestions that are appropriate
        for dyslexic students, with clear instructions and accessibility features.
        
        Args:
            topic: Educational topic or concept to create exercises for
            grade_level: Optional grade level specification (e.g., "élémentaire", "collège")
        
        Returns:
            Dict: Same format as query() method with exercise ideas and instructions
        
        Example:
            >>> rag.get_exercise_ideas("phonétique", "élémentaire")
        """
        
        grade_part = f" pour les élèves de {grade_level}" if grade_level else ""
        question = f"Quels sont des exercices et activités efficaces et adaptés aux dyslexiques pour enseigner {topic}{grade_part} ? Veuillez fournir des exemples spécifiques avec des instructions claires."
        
        return self.query(question)
    
    def get_assessment_adaptations(self, assessment_type: str) -> Dict[str, Any]:
        """
        Get suggestions for adapting assessments for dyslexic students.
        
        Provides specific modifications and alternative assessment methods
        that maintain academic rigor while being accessible to dyslexic students.
        
        Args:
            assessment_type: Type of assessment to adapt (e.g., "tests écrits", "examens oraux")
        
        Returns:
            Dict: Same format as query() method with assessment adaptation recommendations
        
        Example:
            >>> rag.get_assessment_adaptations("tests à choix multiples")
        """
        
        question = f"Comment dois-je modifier les évaluations de type {assessment_type} pour les rendre plus accessibles aux élèves dyslexiques ? Quelles méthodes d'évaluation alternatives sont efficaces ?"
        
        return self.query(question)

def format_response(response: Dict[str, Any]) -> str:
    """
    Format RAG system response for console display.
    
    Creates a well-structured, readable format for displaying AI-generated
    educational recommendations along with source citations.
    
    Args:
        response: Response dictionary from DyslexiaRAG.query() or related methods
    
    Returns:
        str: Formatted response ready for console output with headers,
             content sections, and source citations
    """
    output = []
    
    output.append("=" * 60)
    output.append("ASSISTANT PÉDAGOGIQUE DYSLEXIE")
    output.append("=" * 60)
    
    output.append(f"\nQUESTION : {response['question']}")
    output.append("\nRÉPONSE :")
    output.append(response['answer'])
    
    if response['sources']:
        output.append("\n" + "=" * 40)
        output.append("SOURCES :")
        for i, source in enumerate(response['sources'], 1):
            output.append(f"{i}. {source['source']} par {source['author']}")
            output.append(f"   Section : {source['section']}, Page : {source['page']}")
            output.append(f"   Score de pertinence : {source['relevance_score']:.3f}")
    
    return "\n".join(output)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the RAG system
    rag = DyslexiaRAG()
    
    # Test questions that teachers might ask
    test_questions = [
        "Comment puis-je adapter les exercices de lecture pour les élèves dyslexiques ?",
        "Quelles sont les meilleures façons de présenter les consignes écrites aux élèves dyslexiques ?",
        "Comment dois-je modifier les problèmes de mathématiques pour les élèves dyslexiques ?",
        "Quelles techniques multisensorielles fonctionnent bien pour enseigner l'orthographe aux enfants dyslexiques ?"
    ]
    
    print("Test du Système RAG Dyslexie")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nTest : {question}")
        response = rag.query(question)
        
        if response['sources']:
            print(f"✓ Trouvé {len(response['sources'])} sources pertinentes")
            print(f"✓ Réponse générée : {len(response['answer'])} caractères")
        else:
            print("⚠ Aucune source trouvée - assurez-vous d'avoir téléchargé les documents d'abord")
        
        print("-" * 30)
    
    # Test specific helper methods
    print("\nTest des suggestions d'adaptation spécifiques :")
    
    adaptation_response = rag.suggest_adaptations("mathématiques", "compréhension de lecture")
    exercise_response = rag.get_exercise_ideas("phonétique", "élémentaire")
    assessment_response = rag.get_assessment_adaptations("tests écrits")
    
    print("✓ Suggestions d'adaptation générées")
    print("✓ Idées d'exercices générées") 
    print("✓ Adaptations d'évaluation générées") 