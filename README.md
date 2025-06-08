# Système RAG Dyslexie 🎓

Un système de Génération Augmentée par Récupération (RAG) alimenté par l'IA, conçu pour aider les enseignants à adapter leurs cours, exercices et instructions pour les élèves dyslexiques. Le système utilise des articles de recherche académique sur la dyslexie pour fournir des recommandations pédagogiques fondées sur des preuves.

## 🎯 Objectif

Ce système aide les enseignants en :
- Fournissant des adaptations fondées sur des preuves pour le matériel de cours
- Suggérant des exercices et activités adaptés aux dyslexiques
- Offrant des recommandations d'aménagements d'évaluation
- Tirant des enseignements de la recherche académique sur l'éducation de la dyslexie

## 🏗️ Architecture

The system consists of several components:

1. **PDF Processor** (`pdf_processor.py`) - Extracts and chunks text from academic papers while preserving document structure
2. **Vector Store** (`vector_store.py`) - Manages OpenAI embeddings and Pinecone vector database operations
3. **RAG System** (`rag_system.py`) - Combines semantic search with GPT-4o to generate teaching recommendations
4. **Main Interface** (`main.py`) - Command-line interface for all operations

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key (already configured in `pinecone.api.txt`)
- Academic PDF papers about dyslexia in the `pdf/` directory

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   Or update the `config.py` file directly.

3. **Verify your Pinecone setup:**
   The Pinecone API key is already configured in `pinecone.api.txt`. The system will automatically create an index called `dyslexia-research`.

4. **Process your PDF documents:**
   ```bash
   python main.py setup
   ```
   This will:
   - Extract text from all PDFs in the `pdf/` directory
   - Generate embeddings using OpenAI
   - Upload everything to Pinecone

## 📖 Utilisation

### Mode Interactif (Recommandé)
```bash
python main.py interactive
```

Cela démarre une session interactive où vous pouvez poser des questions comme :
- "Comment puis-je adapter les exercices de lecture pour les élèves dyslexiques ?"
- "Quelles sont les techniques d'enseignement multisensorielles efficaces ?"
- "Comment dois-je modifier les consignes écrites pour les apprenants dyslexiques ?"

### Requêtes en Ligne de Commande
```bash
# Poser une question spécifique
python main.py query "Comment adapter les problèmes de maths pour les élèves dyslexiques ?"

# Obtenir des suggestions d'adaptation pour une matière/activité
python main.py adapt mathématiques "compréhension de lecture"

# Obtenir des idées d'exercices pour un sujet
python main.py exercises phonétique élémentaire

# Obtenir des recommandations d'adaptation d'évaluation
python main.py assessment "tests écrits"
```

### Exemples de Questions que les Enseignants Peuvent Poser

1. **Adaptations de Cours :**
   - "Comment puis-je rendre mes cours d'histoire plus accessibles aux élèves dyslexiques ?"
   - "Quelles modifications dois-je apporter aux instructions de travaux pratiques de sciences ?"

2. **Conception d'Exercices :**
   - "Quelles sont quelques activités d'orthographe adaptées aux dyslexiques ?"
   - "Comment puis-je adapter les exercices de compréhension de lecture ?"

3. **Aménagements d'Évaluation :**
   - "Comment dois-je modifier les tests à choix multiples pour les élèves dyslexiques ?"
   - "Quelles sont les alternatives aux dissertations écrites pour l'évaluation ?"

4. **Technologie et Outils :**
   - "Quelles technologies d'assistance aident les élèves dyslexiques ?"
   - "Quelles polices et mise en forme fonctionnent le mieux pour les lecteurs dyslexiques ?"

## 📁 File Structure

```
dys-ai/
├── config.py              # Configuration settings
├── pdf_processor.py       # PDF text extraction with structure preservation  
├── vector_store.py        # OpenAI embeddings + Pinecone operations
├── rag_system.py         # Main RAG query system
├── main.py               # Command-line interface
├── requirements.txt      # Python dependencies
├── pinecone.api.txt     # Pinecone API key
├── README.md            # This file
└── pdf/                 # Directory containing research PDFs
    ├── Site sur la dyslexie (notioni- concept)/
    └── Memoire sur la dyslexie/
```

## ⚙️ Configuration

The `config.py` file contains important settings:

- **Embedding Model:** `text-embedding-3-small` (1536 dimensions)
- **Chat Model:** `gpt-4o` 
- **Chunk Size:** 1000 tokens with 200 token overlap
- **Retrieval:** Top 5 most relevant chunks per query

You can modify these settings based on your needs and API limits.

## 🔍 How It Works

1. **Document Processing:**
   - PDFs are processed to extract text while preserving academic structure
   - Text is chunked by sections/paragraphs with metadata (author, source, section)
   - Each chunk is converted to embeddings using OpenAI

2. **Storage:**
   - Embeddings and metadata are stored in Pinecone vector database
   - Each vector includes the text content and source information

3. **Query Processing:**
   - Teacher questions are converted to embeddings
   - Semantic search finds most relevant research chunks
   - GPT-4o generates practical teaching advice based on the research context

4. **Response Generation:**
   - AI provides specific, actionable recommendations
   - Responses include citations to source documents
   - Focus on practical classroom applications

## 🎯 Specialized Features

- **Academic Structure Preservation:** Maintains sections, chapters, and paper organization
- **Author & Source Tracking:** Every recommendation includes proper citations
- **Teacher-Focused Prompts:** AI responses specifically target teaching adaptations
- **Multi-Modal Suggestions:** Emphasizes multi-sensory learning approaches
- **Assessment Accommodations:** Specific guidance for test modifications

## 🔧 Troubleshooting

**No search results found:**
- Ensure PDFs have been processed: `python main.py setup`
- Check that your Pinecone index has data: Type `stats` in interactive mode

**API Key errors:**
- Verify your OpenAI API key is set correctly
- Check that `pinecone.api.txt` contains your Pinecone API key

**PDF processing issues:**
- Ensure PDFs are readable (not scanned images without OCR)
- Check that PDFs are in the `pdf/` directory or subdirectories

**Embedding errors:**
- Large chunks might exceed token limits - the system handles this automatically
- Check your OpenAI API rate limits and billing

## 🤝 Contributing

This system is designed to support teachers working with dyslexic students. Contributions that improve:
- PDF processing accuracy
- Teaching recommendation quality  
- User interface usability
- Academic citation handling

are welcome!

## 📝 License

This project is designed for educational use to support inclusive teaching practices. 