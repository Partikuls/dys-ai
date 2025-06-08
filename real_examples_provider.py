#!/usr/bin/env python3
"""
Fournisseur d'Exemples Réels d'Adaptation
Utilise les exemples extraits des cours réels pour améliorer les adaptations
"""

import json
import random
from typing import List, Dict, Optional

class RealExamplesProvider:
    def __init__(self, examples_file: str = "real_adaptation_examples.json"):
        self.examples_file = examples_file
        self.examples = self._load_examples()
    
    def _load_examples(self) -> Dict:
        """Charge les exemples depuis le fichier JSON"""
        try:
            with open(self.examples_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Fichier d'exemples {self.examples_file} non trouvé")
            return {"sections": [], "metadata": {}}
        except Exception as e:
            print(f"❌ Erreur chargement exemples : {e}")
            return {"sections": [], "metadata": {}}
    
    def get_section_example(self, subject: str = None) -> str:
        """Récupère un exemple de section adapté"""
        if not self.examples.get("sections"):
            return ""
        
        # Filtrer par matière si spécifiée
        available_examples = self.examples["sections"]
        if subject:
            available_examples = [
                ex for ex in self.examples["sections"]
                if subject.lower() in ex.get("subject", "").lower()
            ]
            
            # Si pas d'exemple pour cette matière, prendre tous
            if not available_examples:
                available_examples = self.examples["sections"]
        
        # Prendre un exemple aléatoire
        example = random.choice(available_examples)
        
        return self._format_section_example(example)
    
    def _format_section_example(self, example: Dict) -> str:
        """Formate un exemple de section pour le prompt"""
        return f"""
EXEMPLE D'ADAPTATION RÉELLE :

TEXTE ORIGINAL :
{example['original']}

TEXTE ADAPTÉ POUR DYSLEXIQUES :
{example['adapted']}

MAINTENANT, ADAPTE TON TEXTE DE LA MÊME FAÇON :
"""
    
    def get_multiple_examples(self, count: int = 2, subject: str = None) -> str:
        """Récupère plusieurs exemples pour enrichir le prompt"""
        if not self.examples.get("sections") or len(self.examples["sections"]) == 0:
            return ""
        
        # Filtrer par matière
        available_examples = self.examples["sections"]
        if subject:
            subject_examples = [
                ex for ex in self.examples["sections"]
                if subject.lower() in ex.get("subject", "").lower()
            ]
            if subject_examples:
                available_examples = subject_examples
        
        # Sélectionner des exemples variés
        selected_examples = random.sample(
            available_examples, 
            min(count, len(available_examples))
        )
        
        formatted_examples = ""
        for i, example in enumerate(selected_examples, 1):
            formatted_examples += f"""
EXEMPLE {i} D'ADAPTATION RÉELLE :

AVANT (texte original) :
{example['original']}

APRÈS (texte adapté) :
{example['adapted']}

"""
        
        formatted_examples += "MAINTENANT, ADAPTE TON CONTENU EN SUIVANT CES EXEMPLES :\n"
        return formatted_examples
    
    def get_best_example_for_content(self, content: str, subject: str = None) -> str:
        """Trouve le meilleur exemple basé sur la similarité du contenu"""
        if not self.examples.get("sections"):
            return self.get_section_example(subject)
        
        # Filtrer par matière
        candidates = self.examples["sections"]
        if subject:
            subject_candidates = [
                ex for ex in candidates
                if subject.lower() in ex.get("subject", "").lower()
            ]
            if subject_candidates:
                candidates = subject_candidates
        
        # Calculer la similarité (simple basé sur les mots communs)
        content_words = set(content.lower().split())
        best_example = None
        best_score = 0
        
        for example in candidates:
            original_words = set(example['original'].lower().split())
            score = len(content_words.intersection(original_words))
            
            if score > best_score:
                best_score = score
                best_example = example
        
        if best_example:
            return self._format_section_example(best_example)
        else:
            return self.get_section_example(subject)
    
    def has_examples(self) -> bool:
        """Vérifie si des exemples sont disponibles"""
        return len(self.examples.get("sections", [])) > 0
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques des exemples"""
        if not self.examples.get("metadata"):
            return {
                "total_examples": len(self.examples.get("sections", [])),
                "subjects": [],
                "sources": []
            }
        
        # Compter les matières et sources
        subjects = set()
        sources = set()
        
        for example in self.examples.get("sections", []):
            if example.get("subject"):
                subjects.add(example["subject"])
            if example.get("source"):
                sources.add(example["source"])
        
        return {
            "total_examples": len(self.examples.get("sections", [])),
            "subjects": list(subjects),
            "sources": list(sources),
            "metadata": self.examples.get("metadata", {})
        }
    
    def preview_examples(self, count: int = 3):
        """Affiche un aperçu des exemples disponibles"""
        stats = self.get_stats()
        
        print("📚 Exemples d'adaptation réels disponibles :")
        print(f"   • Total : {stats['total_examples']} exemples")
        print(f"   • Matières : {', '.join(stats['subjects'])}")
        print(f"   • Sources : {len(stats['sources'])} cours différents")
        
        if self.examples.get("sections"):
            print(f"\n👀 Aperçu de {min(count, len(self.examples['sections']))} exemples :")
            
            for i, example in enumerate(self.examples["sections"][:count], 1):
                print(f"\n{i}. {example.get('subject', 'N/A')} - {example.get('source', 'N/A')}")
                print(f"   Original : {example['original'][:80]}...")
                print(f"   Adapté   : {example['adapted'][:80]}...")

# Fonction utilitaire pour l'intégration facile
def get_real_example_for_prompt(content_type: str, content: str = "", subject: str = None) -> str:
    """Fonction simple pour obtenir un exemple réel pour n'importe quel prompt"""
    provider = RealExamplesProvider()
    
    if not provider.has_examples():
        return ""
    
    if content_type == "section" and content:
        return provider.get_best_example_for_content(content, subject)
    else:
        return provider.get_section_example(subject)

if __name__ == "__main__":
    # Test du système
    provider = RealExamplesProvider()
    provider.preview_examples()
    
    if provider.has_examples():
        print("\n🧪 Test d'exemple :")
        example = provider.get_section_example("Histoire")
        print(example[:300] + "...")
    else:
        print("\n⚠️  Aucun exemple disponible. Exécutez d'abord real_examples_extractor.py") 