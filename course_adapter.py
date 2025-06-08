#!/usr/bin/env python3
"""
Adaptateur de Cours pour Dyslexiques
Analyse les cours existants et génère des versions adaptées aux élèves dyslexiques
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

from rag_system import DyslexiaRAG
from pdf_processor import PDFProcessor
from config import config
from real_examples_provider import get_real_example_for_prompt

class CourseAdapter:
    def __init__(self):
        self.rag_system = DyslexiaRAG()
        self.pdf_processor = PDFProcessor()
        self.courses_dir = "pdf-cours"
        self.output_dir = "cours-adaptes"
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_course_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extraire le contenu structuré d'un cours"""
        print(f"📚 Analyse du cours : {Path(pdf_path).name}")
        
        doc = fitz.open(pdf_path)
        course_content = {
            "title": Path(pdf_path).stem,
            "total_pages": len(doc),
            "sections": [],
            "full_text": "",
            "key_concepts": [],
            "exercises": [],
            "instructions": []
        }
        
        all_text = ""
        current_section = ""
        current_text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            all_text += text + "\n"
            
            # Détecter les sections (titres en majuscules ou numérotés)
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if self._is_section_header(line):
                    if current_section and current_text:
                        course_content["sections"].append({
                            "title": current_section,
                            "content": current_text.strip(),
                            "page": page_num
                        })
                    current_section = line
                    current_text = ""
                else:
                    current_text += line + "\n"
        
        # Ajouter la dernière section
        if current_section and current_text:
            course_content["sections"].append({
                "title": current_section,
                "content": current_text.strip(),
                "page": len(doc)
            })
        
        course_content["full_text"] = all_text
        doc.close()
        
        # Analyser le contenu pour identifier les éléments clés
        self._analyze_course_elements(course_content)
        
        return course_content
    
    def _is_section_header(self, line: str) -> bool:
        """Détecter si une ligne est un titre de section"""
        if len(line) < 3 or len(line) > 100:
            return False
        
        # Patterns de titres de section
        patterns = [
            line.isupper() and len(line.split()) <= 8,  # Tout en majuscules
            line.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')),  # Numérotation romaine
            line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')),  # Numérotation
            line.startswith(('A.', 'B.', 'C.', 'D.', 'E.')),  # Lettres
            line.startswith(('Chapitre', 'CHAPITRE', 'Leçon', 'LEÇON'))
        ]
        
        return any(patterns)
    
    def _simplify_title(self, title: str) -> str:
        """Simplifier un titre pour les dyslexiques"""
        # Raccourcir et simplifier les titres trop longs ou complexes
        title = title.strip()
        
        # Remplacer certains mots complexes
        replacements = {
            "Analyse": "Étude",
            "Caractéristiques": "Points importants",
            "Méthodologie": "Méthode",
            "Problématique": "Problème",
            "Synthèse": "Résumé"
        }
        
        for old, new in replacements.items():
            title = title.replace(old, new)
        
        # Limiter la longueur
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def _analyze_course_elements(self, course_content: Dict[str, Any]):
        """Analyser le cours pour identifier concepts, exercices, instructions"""
        text = course_content["full_text"].lower()
        
        # Identifier les mots-clés d'exercices
        exercise_keywords = ['exercice', 'activité', 'travail', 'devoir', 'question', 'répondez', 'complétez', 'analysez']
        instruction_keywords = ['consigne', 'instruction', 'lisez', 'écrivez', 'expliquez', 'décrivez', 'comparez']
        
        lines = course_content["full_text"].split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in exercise_keywords):
                if len(line) > 10 and len(line) < 200:
                    course_content["exercises"].append(line.strip())
            
            if any(keyword in line_lower for keyword in instruction_keywords):
                if len(line) > 10 and len(line) < 200:
                    course_content["instructions"].append(line.strip())
    
    def generate_adaptations(self, course_content: Dict[str, Any]) -> Dict[str, Any]:
        """Générer les adaptations dyslexiques pour le cours"""
        print(f"🔄 Génération des adaptations pour : {course_content['title']}")
        
        adaptations = {
            "course_title": course_content["title"],
            "original_sections": len(course_content["sections"]),
            "adapted_sections": [],
            "general_adaptations": {},
            "exercise_adaptations": [],
            "instruction_adaptations": [],
            "formatting_recommendations": {},
            "assessment_adaptations": {}
        }
        
        # 1. Introduction adaptée pour le cours
        real_example = get_real_example_for_prompt("section", "", "Histoire")
        
        intro_query = f"""{real_example}

Réécris une introduction adaptée aux élèves dyslexiques pour un cours sur '{course_content['title']}'. Crée directement le texte d'introduction du cours adapté, avec un langage simple, des phrases courtes et une structure claire.

COURS À ADAPTER : {course_content['title']}"""
        
        intro_response = self.rag_system.query(intro_query)
        adaptations["general_adaptations"] = {
            "adapted_introduction": intro_response["answer"],
            "sources": intro_response["sources"]
        }
        
        # 2. Adapter chaque section
        for i, section in enumerate(course_content["sections"][:3]):  # Limiter à 3 sections pour éviter trop d'appels API
            print(f"   📖 Section {i+1}/{min(3, len(course_content['sections']))}: {section['title'][:50]}...")
            
            # Obtenir un exemple réel similaire au contenu
            real_example = get_real_example_for_prompt("section", section['content'][:200], "Histoire")
            
            section_query = f"""{real_example}

TITRE ORIGINAL: {section['title']}
CONTENU ORIGINAL: {section['content'][:800]}...

INSTRUCTIONS: Réécris cette section avec :
- Phrases courtes et simples
- Vocabulaire accessible 
- Structure claire avec des sous-titres
- Exemples concrets
- Points clés mis en évidence

CRÉE LE TEXTE ADAPTÉ DE LA SECTION:"""
            
            section_response = self.rag_system.query(section_query)
            
            adapted_section = {
                "original_title": section["title"],
                "adapted_title": self._simplify_title(section["title"]),
                "original_content_preview": section["content"][:200] + "...",
                "adapted_content": section_response["answer"],
                "sources": section_response["sources"],
                "page": section["page"]
            }
            
            adaptations["adapted_sections"].append(adapted_section)
        
        # 3. Adapter les exercices
        for exercise in course_content["exercises"][:3]:  # Limiter à 3 exercices
            real_example = get_real_example_for_prompt("section", exercise, "Histoire")
            
            exercise_query = f"""{real_example}

EXERCICE ORIGINAL: {exercise}

INSTRUCTIONS: Crée un exercice adapté avec :
- Consignes claires et courtes
- Instructions étape par étape
- Vocabulaire simple
- Aide visuelle ou structurée si nécessaire

CRÉE L'EXERCICE ADAPTÉ:"""
            
            exercise_response = self.rag_system.query(exercise_query)
            
            adaptations["exercise_adaptations"].append({
                "original_exercise": exercise,
                "adapted_exercise": exercise_response["answer"],
                "sources": exercise_response["sources"]
            })
        
        # 4. Adapter les consignes
        for instruction in course_content["instructions"][:3]:  # Limiter à 3 consignes
            real_example = get_real_example_for_prompt("section", instruction, "Histoire")
            
            instruction_query = f"""{real_example}

CONSIGNE ORIGINALE: {instruction}

INSTRUCTIONS: Réécris la consigne avec :
- Mots simples et précis
- Une seule instruction par phrase
- Ordre logique des étapes
- Éviter les négations complexes

CRÉE LA CONSIGNE ADAPTÉE:"""
            
            instruction_response = self.rag_system.query(instruction_query)
            
            adaptations["instruction_adaptations"].append({
                "original_instruction": instruction,
                "adapted_instruction": instruction_response["answer"],
                "sources": instruction_response["sources"]
            })
        
        # 5. Guide de mise en forme adapté
        formatting_query = f"Crée un guide de mise en forme spécifique pour ce cours '{course_content['title']}' adapté aux dyslexiques. Donne des instructions concrètes et pratiques pour la présentation du document."
        
        formatting_response = self.rag_system.query(formatting_query)
        adaptations["formatting_recommendations"] = {
            "guide": formatting_response["answer"],
            "sources": formatting_response["sources"]
        }
        
        # 6. Exemple d'évaluation adaptée
        assessment_query = f"Crée un exemple concret d'évaluation adaptée pour ce cours '{course_content['title']}' destinée aux élèves dyslexiques. Produis un modèle d'exercice d'évaluation avec les adaptations nécessaires."
        
        assessment_response = self.rag_system.query(assessment_query)
        adaptations["assessment_adaptations"] = {
            "example_assessment": assessment_response["answer"],
            "sources": assessment_response["sources"]
        }
        
        return adaptations
    
    def save_adaptations(self, adaptations: Dict[str, Any], output_format: str = "markdown"):
        """Sauvegarder les adaptations dans un fichier"""
        filename = f"{adaptations['course_title']}_adapte_dyslexie"
        
        if output_format == "markdown":
            self._save_as_markdown(adaptations, filename)
        elif output_format == "json":
            self._save_as_json(adaptations, filename)
        else:
            self._save_as_text(adaptations, filename)
    
    def _save_as_markdown(self, adaptations: Dict[str, Any], filename: str):
        """Sauvegarder en format Markdown"""
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {adaptations['course_title']} - Version Adaptée aux Dyslexiques\n\n")
            f.write(f"*Version adaptée générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n\n")
            f.write("---\n\n")
            
            # Introduction adaptée
            f.write("## 📚 Introduction\n\n")
            f.write(adaptations['general_adaptations']['adapted_introduction'])
            f.write("\n\n")
            
            # Sections adaptées
            f.write("## 📖 Contenu du Cours\n\n")
            for i, section in enumerate(adaptations['adapted_sections'], 1):
                # Utiliser le titre adapté si disponible
                title = section.get('adapted_title', section['original_title'])
                f.write(f"### {i}. {title}\n\n")
                
                # Afficher le contenu adapté directement
                f.write(section['adapted_content'])
                f.write("\n\n")
                
                # Optionnel : lien vers l'original
                f.write(f"<details>\n<summary>📄 Voir le contenu original</summary>\n\n")
                f.write(f"{section['original_content_preview']}\n\n")
                f.write(f"</details>\n\n")
                f.write("---\n\n")
            
            # Exercices adaptés
            if adaptations['exercise_adaptations']:
                f.write("## 🎯 Exercices\n\n")
                for i, exercise in enumerate(adaptations['exercise_adaptations'], 1):
                    f.write(f"### Exercice {i}\n\n")
                    f.write(exercise['adapted_exercise'])
                    f.write("\n\n")
                    
                    # Exercice original en détails
                    f.write(f"<details>\n<summary>📄 Voir l'exercice original</summary>\n\n")
                    f.write(f"{exercise['original_exercise']}\n\n")
                    f.write(f"</details>\n\n")
                    f.write("---\n\n")
            
            # Consignes adaptées
            if adaptations['instruction_adaptations']:
                f.write("## 📝 Instructions et Consignes\n\n")
                for i, instruction in enumerate(adaptations['instruction_adaptations'], 1):
                    f.write(f"### Consigne {i}\n\n")
                    f.write(instruction['adapted_instruction'])
                    f.write("\n\n")
                    
                    # Consigne originale en détails
                    f.write(f"<details>\n<summary>📄 Voir la consigne originale</summary>\n\n")
                    f.write(f"{instruction['original_instruction']}\n\n")
                    f.write(f"</details>\n\n")
                    f.write("---\n\n")
            
            # Guide de mise en forme
            f.write("## 🎨 Guide de Présentation\n\n")
            f.write(adaptations['formatting_recommendations']['guide'])
            f.write("\n\n")
            
            # Exemple d'évaluation
            f.write("## 📊 Exemple d'Évaluation Adaptée\n\n")
            f.write(adaptations['assessment_adaptations']['example_assessment'])
            f.write("\n\n")
            
            f.write("---\n\n")
            f.write("*Cette version adaptée a été générée automatiquement en utilisant la recherche sur la dyslexie. Elle doit être révisée par un enseignant avant utilisation.*\n")
        
        print(f"✅ Adaptations sauvegardées : {filepath}")
    
    def _save_as_json(self, adaptations: Dict[str, Any], filename: str):
        """Sauvegarder en format JSON"""
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        
        adaptations["generated_at"] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(adaptations, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Adaptations sauvegardées : {filepath}")
    
    def _save_as_text(self, adaptations: Dict[str, Any], filename: str):
        """Sauvegarder en format texte simple"""
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"COURS ADAPTÉ POUR DYSLEXIQUES : {adaptations['course_title']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n")
            
            f.write("ADAPTATIONS GÉNÉRALES :\n")
            f.write("-" * 25 + "\n")
            f.write(adaptations['general_adaptations']['recommendations'])
            f.write("\n\n")
            
            # Continuer avec les autres sections...
        
        print(f"✅ Adaptations sauvegardées : {filepath}")
    
    def process_all_courses(self, output_format: str = "markdown"):
        """Traiter tous les cours dans le répertoire pdf-cours"""
        courses_path = Path(self.courses_dir)
        
        if not courses_path.exists():
            print(f"❌ Répertoire {self.courses_dir} non trouvé")
            return
        
        pdf_files = list(courses_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ Aucun fichier PDF trouvé dans {self.courses_dir}")
            return
        
        print(f"🚀 Traitement de {len(pdf_files)} cours...")
        print("=" * 60)
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📚 Cours {i}/{len(pdf_files)} : {pdf_file.name}")
            
            try:
                # Extraire le contenu
                course_content = self.extract_course_content(str(pdf_file))
                
                # Générer les adaptations
                adaptations = self.generate_adaptations(course_content)
                
                # Sauvegarder
                self.save_adaptations(adaptations, output_format)
                
                print(f"✅ Cours {pdf_file.name} traité avec succès")
                
            except Exception as e:
                print(f"❌ Erreur lors du traitement de {pdf_file.name}: {e}")
        
        print(f"\n🎉 Traitement terminé ! Résultats dans le dossier '{self.output_dir}'")

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptateur de Cours pour Dyslexiques")
    parser.add_argument('--format', choices=['markdown', 'json', 'text'], default='markdown',
                       help='Format de sortie (défaut: markdown)')
    parser.add_argument('--course', type=str, help='Traiter un cours spécifique (nom du fichier)')
    
    args = parser.parse_args()
    
    adapter = CourseAdapter()
    
    if args.course:
        # Traiter un cours spécifique
        course_path = os.path.join(adapter.courses_dir, args.course)
        if os.path.exists(course_path):
            print(f"🎯 Traitement du cours spécifique : {args.course}")
            course_content = adapter.extract_course_content(course_path)
            adaptations = adapter.generate_adaptations(course_content)
            adapter.save_adaptations(adaptations, args.format)
        else:
            print(f"❌ Cours {args.course} non trouvé dans {adapter.courses_dir}")
    else:
        # Traiter tous les cours
        adapter.process_all_courses(args.format)

if __name__ == "__main__":
    main() 