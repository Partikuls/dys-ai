#!/usr/bin/env python3
"""
Dyslexia RAG System - Main Application
Helps teachers adapt courses for dyslexic students using research-based AI assistance
"""

import argparse
import sys
from pathlib import Path

from pdf_processor import PDFProcessor
from vector_store import VectorStore
from rag_system import DyslexiaRAG, format_response
from config import config

def setup_database():
    """Process PDFs and upload to Pinecone vector database"""
    print("🔄 Configuration de la Base de Données de Recherche sur la Dyslexie")
    print("=" * 60)
    
    # Step 1: Process PDFs
    print("Étape 1 : Traitement des documents PDF...")
    processor = PDFProcessor()
    chunks = processor.process_all_pdfs()
    
    if not chunks:
        print("❌ Aucun document PDF trouvé. Veuillez vous assurer que les PDFs sont dans le dossier 'pdf'.")
        return False
    
    print(f"✅ {len(chunks)} segments de texte extraits avec succès des PDFs")
    
    # Step 2: Upload to Pinecone
    print("\nÉtape 2 : Téléchargement vers la base de données vectorielle...")
    vector_store = VectorStore()
    vector_store.upload_chunks_to_pinecone(chunks)
    
    print("✅ Configuration de la base de données terminée !")
    return True

def interactive_query_mode():
    """Interactive mode for asking questions about dyslexia adaptations"""
    print("\n🎓 Assistant Pédagogique Dyslexie - Mode Interactif")
    print("=" * 55)
    print("Posez des questions sur l'adaptation des cours pour les élèves dyslexiques.")
    print("Tapez 'quitter' pour sortir, 'aide' pour des exemples, ou 'stats' pour les infos de la base.")
    print("-" * 55)
    
    rag = DyslexiaRAG()
    
    while True:
        try:
            question = input("\n📝 Votre question : ").strip()
            
            if question.lower() in ['quitter', 'quit', 'exit', 'q', 'sortir']:
                print("👋 Au revoir ! Bon enseignement !")
                break
            
            elif question.lower() in ['aide', 'help']:
                show_example_questions()
                continue
            
            elif question.lower() == 'stats':
                try:
                    stats = rag.vector_store.get_index_stats()
                    print(f"\n📊 Statistiques de la Base de Données :")
                    print(f"   Total de vecteurs : {stats.get('total_vector_count', 'Inconnu')}")
                    print(f"   Dimensions : {stats.get('dimension', 'Inconnu')}")
                except Exception as e:
                    print(f"❌ Erreur lors de la récupération des stats : {e}")
                continue
            
            elif not question:
                continue
            
            print("\n🔍 Recherche dans la base de données de recherche...")
            response = rag.query(question)
            
            print("\n" + format_response(response))
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir ! Bon enseignement !")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}")

def show_example_questions():
    """Show example questions teachers can ask"""
    examples = [
        "Comment puis-je adapter les exercices de lecture pour les élèves dyslexiques ?",
        "Quelles sont les techniques d'enseignement multisensorielles efficaces pour la dyslexie ?",
        "Comment dois-je modifier les consignes écrites pour les apprenants dyslexiques ?",
        "Quels aménagements fonctionnent le mieux pour les évaluations de maths avec les élèves dyslexiques ?",
        "Comment puis-je rendre les devoirs d'écriture plus accessibles aux élèves dyslexiques ?",
        "Quelles sont les meilleures polices et mise en forme pour les lecteurs dyslexiques ?",
        "Comment adapter l'enseignement de la phonétique pour les enfants dyslexiques ?",
        "Quelles technologies d'assistance aident les élèves dyslexiques en classe ?"
    ]
    
    print("\n💡 Exemples de Questions :")
    print("-" * 35)
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")

def quick_query(question: str):
    """Answer a single question and exit"""
    print(f"🔍 Réponse à : {question}")
    print("=" * 50)
    
    rag = DyslexiaRAG()
    response = rag.query(question)
    
    print(format_response(response))

def get_specific_help(command_type: str, *args):
    """Get specific types of help based on command"""
    rag = DyslexiaRAG()
    
    if command_type == "adapt":
        if len(args) < 2:
            print("Usage : python main.py adapt <matière> <type_activité>")
            print("Exemple : python main.py adapt mathématiques 'compréhension de lecture'")
            return
        
        subject, activity_type = args[0], args[1]
        response = rag.suggest_adaptations(subject, activity_type)
        
    elif command_type == "exercises":
        if len(args) < 1:
            print("Usage : python main.py exercises <sujet> [niveau_scolaire]")
            print("Exemple : python main.py exercises phonétique élémentaire")
            return
        
        topic = args[0]
        grade_level = args[1] if len(args) > 1 else ""
        response = rag.get_exercise_ideas(topic, grade_level)
        
    elif command_type == "assessment":
        if len(args) < 1:
            print("Usage : python main.py assessment <type_évaluation>")
            print("Exemple : python main.py assessment 'tests écrits'")
            return
        
        assessment_type = args[0]
        response = rag.get_assessment_adaptations(assessment_type)
    
    else:
        print(f"Commande inconnue : {command_type}")
        return
    
    print(format_response(response))

def main():
    parser = argparse.ArgumentParser(
        description="Système RAG Dyslexie - Assistant IA pour les Adaptations Pédagogiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py setup                    # Traiter les PDFs et configurer la base
  python main.py interactive              # Démarrer le mode questions interactif
  python main.py query "Comment adapter les exercices de lecture ?"
  python main.py adapt mathématiques "problèmes de mots"
  python main.py exercises phonétique élémentaire
  python main.py assessment "tests écrits"
        """
    )
    
    parser.add_argument('command', nargs='?', default='interactive',
                       help='Commande à exécuter (setup, interactive, query, adapt, exercises, assessment)')
    parser.add_argument('args', nargs='*', help='Arguments supplémentaires pour la commande')
    
    args = parser.parse_args()
    
    # Check if we have necessary API keys
    if config.OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ Veuillez définir votre clé API OpenAI dans la variable d'environnement OPENAI_API_KEY")
        print("   ou mettre à jour le fichier config.py")
        return
    
    if config.PINECONE_API_KEY == "your-pinecone-api-key-here":
        print("❌ Veuillez définir votre clé API Pinecone dans pinecone.api.txt")
        print("   ou dans la variable d'environnement PINECONE_API_KEY")
        return
    
    # Route commands
    if args.command == 'setup':
        setup_database()
    
    elif args.command == 'interactive':
        interactive_query_mode()
    
    elif args.command == 'query':
        if not args.args:
            print("Veuillez fournir une question à poser")
            print("Exemple : python main.py query 'Comment adapter les exercices de lecture ?'")
            return
        question = ' '.join(args.args)
        quick_query(question)
    
    elif args.command in ['adapt', 'exercises', 'assessment']:
        get_specific_help(args.command, *args.args)
    
    else:
        print(f"Commande inconnue : {args.command}")
        print("Utilisez 'python main.py --help' pour les informations d'usage")

if __name__ == "__main__":
    main() 