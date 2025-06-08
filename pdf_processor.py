import fitz  # PyMuPDF
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from config import config

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document with metadata"""
    text: str
    source: str
    author: str
    page_number: int
    section: str
    chunk_id: str

class PDFProcessor:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        """Extract metadata from PDF"""
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        # Extract author, title, etc.
        author = metadata.get('author', 'Unknown Author')
        title = metadata.get('title', Path(pdf_path).stem)
        
        # If no author in metadata, try to extract from first page
        if author == 'Unknown Author' or not author:
            first_page = doc[0].get_text()
            author = self._extract_author_from_text(first_page)
        
        doc.close()
        return {
            'author': author,
            'title': title,
            'source': Path(pdf_path).name
        }
    
    def _extract_author_from_text(self, text: str) -> str:
        """Try to extract author from text using common academic paper patterns"""
        # Look for common author patterns in academic papers
        patterns = [
            r'(?:By|Author[s]?:?)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s*,\s*[A-Z][a-z]+)*\s*$',
            r'([A-Z][A-Z\s\.]+)(?:\s*\n\s*[A-Z][a-z]+\s+University)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:500], re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return 'Unknown Author'
    
    def _detect_sections(self, text: str) -> List[Tuple[str, int]]:
        """Detect section headers in academic papers"""
        lines = text.split('\n')
        sections = []
        
        # Common section patterns in academic papers
        section_patterns = [
            r'^(?:Abstract|Introduction|Literature Review|Methodology|Method|Results|Discussion|Conclusion|References?)$',
            r'^\d+\.?\s*([A-Z][A-Z\s]+)$',
            r'^([A-Z][A-Z\s]{2,20})$',
            r'^\d+\.\d+\.?\s*([A-Z][a-z\s]+)$'
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            for pattern in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    sections.append((line, i))
                    break
        
        return sections
    
    def _chunk_text_by_structure(self, text: str, metadata: Dict[str, str], page_num: int) -> List[DocumentChunk]:
        """Chunk text while preserving document structure"""
        chunks = []
        sections = self._detect_sections(text)
        
        if not sections:
            # No sections detected, chunk by size
            return self._chunk_by_size(text, metadata, page_num, "Content")
        
        current_section = "Introduction"
        current_text = ""
        
        lines = text.split('\n')
        section_index = 0
        
        for i, line in enumerate(lines):
            # Check if this line is a section header
            if section_index < len(sections) and i >= sections[section_index][1]:
                # Save previous section if it has content
                if current_text.strip():
                    chunks.extend(self._chunk_by_size(current_text, metadata, page_num, current_section))
                
                # Start new section
                current_section = sections[section_index][0]
                current_text = ""
                section_index += 1
            
            current_text += line + "\n"
        
        # Add the last section
        if current_text.strip():
            chunks.extend(self._chunk_by_size(current_text, metadata, page_num, current_section))
        
        return chunks
    
    def _chunk_by_size(self, text: str, metadata: Dict[str, str], page_num: int, section: str) -> List[DocumentChunk]:
        """Chunk text by size with overlap"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunk_id = f"{metadata['source']}_page{page_num}_chunk{len(chunks)}"
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    source=metadata['source'],
                    author=metadata['author'],
                    page_number=page_num,
                    section=section,
                    chunk_id=chunk_id
                ))
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        """Process a single PDF and return chunks"""
        print(f"Traitement : {pdf_path}")
        
        metadata = self.extract_metadata(pdf_path)
        doc = fitz.open(pdf_path)
        all_chunks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():  # Only process pages with text
                chunks = self._chunk_text_by_structure(text, metadata, page_num + 1)
                all_chunks.extend(chunks)
        
        doc.close()
        print(f"Extraction de {len(all_chunks)} segments depuis {metadata['title']}")
        return all_chunks
    
    def process_all_pdfs(self, pdf_directory: str = None) -> List[DocumentChunk]:
        """Process all PDFs in the directory and subdirectories"""
        if pdf_directory is None:
            pdf_directory = config.PDF_DIRECTORY
        
        all_chunks = []
        pdf_path = Path(pdf_directory)
        
        # Find all PDF files recursively
        pdf_files = list(pdf_path.rglob("*.pdf"))
        
        if not pdf_files:
            print(f"Aucun fichier PDF trouvé dans {pdf_directory}")
            return []
        
        print(f"Trouvé {len(pdf_files)} fichiers PDF")
        
        for pdf_file in pdf_files:
            try:
                chunks = self.process_pdf(str(pdf_file))
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Erreur lors du traitement de {pdf_file}: {e}")
        
        print(f"Total de segments extraits : {len(all_chunks)}")
        return all_chunks

# Example usage
if __name__ == "__main__":
    processor = PDFProcessor()
    chunks = processor.process_all_pdfs()
    
    if chunks:
        print("\nExemple de segment :")
        print(f"Source : {chunks[0].source}")
        print(f"Auteur : {chunks[0].author}")
        print(f"Section : {chunks[0].section}")
        print(f"Aperçu du texte : {chunks[0].text[:200]}...") 