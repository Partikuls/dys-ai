# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up the RAG system (process PDFs and upload to Pinecone)
python main.py setup

# Configure OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Testing
```bash
# Run basic course adaptation test
python test_course_adaptation.py

# Extract real examples for enhanced testing
python real_examples_extractor.py

# Run advanced test with real examples
python test_with_real_examples.py

# Test individual components
python rag_system.py
python vector_store.py
```

### Running the Application
```bash
# Interactive mode (recommended)
python main.py interactive

# Direct queries
python main.py query "How to adapt reading exercises for dyslexic students?"

# Course adaptation
python main.py adapt mathematics "reading comprehension"

# Exercise suggestions
python main.py exercises phonetics elementary

# Assessment recommendations  
python main.py assessment "written tests"
```

## Architecture Overview

This is a RAG (Retrieval-Augmented Generation) system designed to help teachers adapt educational content for dyslexic students using research-based AI assistance.

### Core Components

1. **PDF Processor** (`pdf_processor.py`): Extracts and chunks text from academic papers while preserving document structure
2. **Vector Store** (`vector_store.py`): Manages OpenAI embeddings and Pinecone vector database operations
3. **RAG System** (`rag_system.py`): Combines semantic search with GPT-4o to generate teaching recommendations
4. **Course Adapter** (`course_adapter.py`): Analyzes existing courses and generates dyslexia-adapted versions
5. **Main Interface** (`main.py`): Command-line interface for all operations

### Data Flow
1. Academic PDFs (in `pdf/` directory) → PDF Processor → Text chunks with metadata
2. Text chunks → OpenAI Embeddings → Pinecone Vector Database  
3. Teacher queries → Semantic search → Relevant research chunks → GPT-4o → Practical recommendations

### Key Configuration (config.py)
- **Models**: `text-embedding-3-small` (embeddings), `gpt-4o` (chat)
- **Chunking**: 1000 tokens with 200 token overlap
- **Retrieval**: Top 5 most relevant chunks per query
- **Pinecone Index**: `dyslexia-research` (auto-created)

### Directory Structure
- `pdf/`: Academic research papers on dyslexia
- `pdf-cours/`: Course materials to be adapted (organized by grade level)
- `cours-adaptes/`: Generated adapted course materials (JSON + Markdown)
- `real_adaptation_examples.json`: Real examples for enhanced adaptations

### Testing Approach
The system uses custom test scripts rather than formal testing frameworks. Tests focus on integration testing of the full pipeline from PDF processing to adaptation generation.

### API Dependencies
- **OpenAI API**: Required for embeddings and chat completions
- **Pinecone API**: Vector database storage (key in `pinecone.api.txt`)