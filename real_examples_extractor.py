#!/usr/bin/env python3
"""
Extracteur d'Exemples Réels d'Adaptation
Analyse les cours avant/après dans pdf-cours-exemple pour créer des exemples d'adaptation
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
import re
from typing import List, Dict, Tuple, Any
import json

class RealExamplesExtractor:
    def __init__(self):
        self.examples_dir = "pdf-cours-exemple"
        self.examples_data = {
            "sections": [],
            "exercises": [],
            "instructions": [],
            "introductions": []
        }
    
    def find_course_pairs(self) -> List[Dict[str, Any]]:
        """Trouve toutes les paires de cours normal/adapté"""
        pairs = []
        
        for level_dir in Path(self.examples_dir).iterdir():
            if level_dir.is_dir() and level_dir.name != ".DS_Store":
                print(f"🔍 Analyse niveau : {level_dir.name}")
                
                for chapter_dir in level_dir.iterdir():
                    if chapter_dir.is_dir():
                        files = list(chapter_dir.glob("*"))
                        
                        # Chercher les paires normal/DYS
                        normal_files = [f for f in files if not self._is_adapted_file(f.name)]
                        adapted_files = [f for f in files if self._is_adapted_file(f.name)]
                        
                        for normal_file in normal_files:
                            # Chercher le fichier adapté correspondant
                            adapted_file = self._find_matching_adapted(normal_file, adapted_files)
                            
                            if adapted_file:
                                pair = {
                                    "level": level_dir.name,
                                    "chapter": chapter_dir.name,
                                    "normal_file": str(normal_file),
                                    "adapted_file": str(adapted_file),
                                    "subject": self._guess_subject(normal_file.name)
                                }
                                pairs.append(pair)
                                print(f"   ✅ Paire trouvée : {normal_file.name} → {adapted_file.name}")
        
        return pairs
    
    def _is_adapted_file(self, filename: str) -> bool:
        """Détermine si un fichier est une version adaptée"""
        indicators = ['dys', 'DYS', 'dyslexie', 'adapté', 'adapte']
        return any(indicator in filename.lower() for indicator in indicators)
    
    def _find_matching_adapted(self, normal_file: Path, adapted_files: List[Path]) -> Path:
        """Trouve le fichier adapté correspondant au fichier normal"""
        normal_name = normal_file.stem.lower()
        
        for adapted_file in adapted_files:
            adapted_name = adapted_file.stem.lower()
            
            # Nettoyer les noms pour la comparaison
            normal_clean = re.sub(r'[^\w\s]', '', normal_name)
            adapted_clean = re.sub(r'[^\w\s]', '', adapted_name)
            adapted_clean = re.sub(r'\b(dys|dyslexie|adapté|adapte)\b', '', adapted_clean)
            
            # Calculer la similarité
            if self._are_similar(normal_clean, adapted_clean.strip()):
                return adapted_file
        
        return None
    
    def _are_similar(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """Calcule si deux noms de fichiers sont similaires"""
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def _guess_subject(self, filename: str) -> str:
        """Devine la matière à partir du nom de fichier"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['guerre', 'revolution', 'histoire', 'civil', 'militaire']):
            return "Histoire"
        elif any(word in filename_lower for word in ['lumiere', 'siècle', 'commerce', 'esclavage']):
            return "Histoire"
        elif any(word in filename_lower for word in ['math', 'equation', 'geometrie']):
            return "Mathématiques"
        elif any(word in filename_lower for word in ['français', 'litterature', 'texte']):
            return "Français"
        elif any(word in filename_lower for word in ['science', 'biologie', 'physique']):
            return "Sciences"
        else:
            return "Histoire"  # Par défaut
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extrait le texte d'un fichier PDF ou DOCX"""
        try:
            if file_path.endswith('.pdf'):
                return self._extract_from_pdf(file_path)
            elif file_path.endswith('.docx'):
                return self._extract_from_docx(file_path)
            else:
                print(f"⚠️  Format non supporté : {file_path}")
                return ""
        except Exception as e:
            print(f"❌ Erreur extraction {file_path}: {e}")
            return ""
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extrait le texte d'un PDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    
    def _extract_from_docx(self, docx_path: str) -> str:
        """Extrait le texte d'un fichier DOCX"""
        try:
            import docx
            doc = docx.Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print("⚠️  Module python-docx requis pour lire les fichiers .docx")
            return ""
        except Exception as e:
            print(f"❌ Erreur lecture DOCX: {e}")
            return ""
    
    def extract_sections_comparison(self, normal_text: str, adapted_text: str) -> List[Dict[str, str]]:
        """Compare les sections entre version normale et adaptée"""
        examples = []
        
        # Diviser les textes en sections approximatives
        normal_sections = self._split_into_sections(normal_text)
        adapted_sections = self._split_into_sections(adapted_text)
        
        # Essayer de faire correspondre les sections
        for i, normal_section in enumerate(normal_sections[:3]):  # Limiter à 3 exemples
            if i < len(adapted_sections):
                adapted_section = adapted_sections[i]
                
                if len(normal_section) > 100 and len(adapted_section) > 50:
                    example = {
                        "original": normal_section[:500] + "..." if len(normal_section) > 500 else normal_section,
                        "adapted": adapted_section[:500] + "..." if len(adapted_section) > 500 else adapted_section
                    }
                    examples.append(example)
        
        return examples
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Divise un texte en sections approximatives"""
        # Chercher les titres et divisions
        lines = text.split('\n')
        sections = []
        current_section = ""
        
        for line in lines:
            line = line.strip()
            
            # Détecter les titres de section
            if self._is_section_title(line):
                if current_section:
                    sections.append(current_section.strip())
                current_section = line + "\n"
            else:
                current_section += line + "\n"
        
        # Ajouter la dernière section
        if current_section:
            sections.append(current_section.strip())
        
        return sections
    
    def _is_section_title(self, line: str) -> bool:
        """Détermine si une ligne est un titre de section"""
        if len(line) < 3 or len(line) > 100:
            return False
        
        # Patterns de titres
        patterns = [
            line.isupper() and len(line.split()) <= 8,
            line.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')),
            line.startswith(('1.', '2.', '3.', '4.', '5.')),
            line.startswith(('A.', 'B.', 'C.', 'D.')),
            re.match(r'^[A-Z][^.]*:?\s*$', line) and len(line.split()) <= 6
        ]
        
        return any(patterns)
    
    def extract_all_examples(self) -> Dict[str, List[Dict]]:
        """Extrait tous les exemples des cours avant/après"""
        pairs = self.find_course_pairs()
        all_examples = {
            "sections": [],
            "metadata": {
                "total_pairs": len(pairs),
                "processed": 0,
                "subjects": []
            }
        }
        
        print(f"\n📚 Extraction d'exemples à partir de {len(pairs)} paires de cours...")
        
        for i, pair in enumerate(pairs, 1):
            print(f"\n🔄 Traitement {i}/{len(pairs)}: {pair['chapter']}")
            
            try:
                # Extraire les textes
                normal_text = self.extract_text_from_file(pair['normal_file'])
                adapted_text = self.extract_text_from_file(pair['adapted_file'])
                
                if normal_text and adapted_text:
                    # Extraire les exemples de sections
                    section_examples = self.extract_sections_comparison(normal_text, adapted_text)
                    
                    for example in section_examples:
                        example['subject'] = pair['subject']
                        example['source'] = f"{pair['level']} - {pair['chapter']}"
                        all_examples['sections'].append(example)
                    
                    print(f"   ✅ {len(section_examples)} exemples extraits")
                    all_examples['metadata']['processed'] += 1
                    
                    if pair['subject'] not in all_examples['metadata']['subjects']:
                        all_examples['metadata']['subjects'].append(pair['subject'])
                
            except Exception as e:
                print(f"   ❌ Erreur : {e}")
        
        return all_examples
    
    def save_examples(self, examples: Dict, filename: str = "real_adaptation_examples.json"):
        """Sauvegarde les exemples extraits"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Exemples sauvegardés dans {filename}")
        print(f"   📊 Total sections : {len(examples['sections'])}")
        print(f"   📝 Paires traitées : {examples['metadata']['processed']}")
        print(f"   📚 Matières : {', '.join(examples['metadata']['subjects'])}")

def main():
    """Point d'entrée principal"""
    extractor = RealExamplesExtractor()
    
    print("🔍 Recherche des cours avant/après...")
    pairs = extractor.find_course_pairs()
    
    if not pairs:
        print("❌ Aucune paire de cours trouvée")
        return
    
    print(f"\n✅ {len(pairs)} paires de cours trouvées")
    
    # Extraire tous les exemples
    examples = extractor.extract_all_examples()
    
    # Sauvegarder
    extractor.save_examples(examples)
    
    # Afficher un aperçu
    if examples['sections']:
        print("\n👀 Aperçu du premier exemple :")
        first_example = examples['sections'][0]
        print(f"   📚 Matière : {first_example['subject']}")
        print(f"   📖 Source : {first_example['source']}")
        print(f"   📝 Original : {first_example['original'][:100]}...")
        print(f"   ✨ Adapté : {first_example['adapted'][:100]}...")

if __name__ == "__main__":
    main() 