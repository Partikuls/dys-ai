#!/usr/bin/env python3
"""
Script de test pour l'adaptation de cours dyslexiques
Test avec le cours Civilsetmilitaires1GM.pdf
"""

from course_adapter import CourseAdapter

def test_single_course():
    """Tester l'adaptation d'un seul cours"""
    
    print("🧪 Test d'Adaptation de Cours pour Dyslexiques")
    print("=" * 50)
    
    # Initialiser l'adaptateur
    adapter = CourseAdapter()
    
    # Cours à tester
    course_file = "Civilsetmilitaires1GM.pdf"
    course_path = f"pdf-cours/{course_file}"
    
    try:
        print(f"📚 Test avec le cours : {course_file}")
        
        # 1. Extraire le contenu
        print("\n🔍 Étape 1 : Extraction du contenu...")
        course_content = adapter.extract_course_content(course_path)
        
        print(f"   ✅ Titre : {course_content['title']}")
        print(f"   ✅ Pages : {course_content['total_pages']}")
        print(f"   ✅ Sections détectées : {len(course_content['sections'])}")
        print(f"   ✅ Exercices trouvés : {len(course_content['exercises'])}")
        print(f"   ✅ Consignes trouvées : {len(course_content['instructions'])}")
        
        # Afficher les premières sections
        if course_content['sections']:
            print("\n📖 Aperçu des sections :")
            for i, section in enumerate(course_content['sections'][:3], 1):
                print(f"   {i}. {section['title'][:60]}...")
        
        # 2. Générer les adaptations
        print("\n🔄 Étape 2 : Génération des adaptations...")
        adaptations = adapter.generate_adaptations(course_content)
        
        # 3. Sauvegarder en plusieurs formats
        print("\n💾 Étape 3 : Sauvegarde des résultats...")
        
        # Sauvegarder en Markdown (pour lecture facile)
        adapter.save_adaptations(adaptations, "markdown")
        
        # Sauvegarder en JSON (pour analyse programmatique)
        adapter.save_adaptations(adaptations, "json")
        
        print("\n🎉 Test terminé avec succès !")
        print(f"📁 Résultats disponibles dans le dossier : {adapter.output_dir}")
        
        # Afficher un résumé
        print("\n📊 Résumé du cours adapté généré :")
        print(f"   • Introduction adaptée : ✅")
        print(f"   • Sections adaptées : {len(adaptations['adapted_sections'])}")
        print(f"   • Exercices adaptés : {len(adaptations['exercise_adaptations'])}")
        print(f"   • Consignes adaptées : {len(adaptations['instruction_adaptations'])}")
        print(f"   • Guide de mise en forme : ✅")
        print(f"   • Exemple d'évaluation : ✅")
        
        # Aperçu du contenu généré
        print("\n👀 Aperçu du contenu adapté :")
        if adaptations['adapted_sections']:
            first_section = adaptations['adapted_sections'][0]
            print(f"   📖 Première section adaptée : {first_section.get('adapted_title', first_section['original_title'])}")
            preview_text = first_section['adapted_content'][:150] + "..." if len(first_section['adapted_content']) > 150 else first_section['adapted_content']
            print(f"   📝 Aperçu : {preview_text}")
        
    except FileNotFoundError:
        print(f"❌ Fichier {course_path} non trouvé")
        print("   Assurez-vous que le fichier existe dans le dossier pdf-cours/")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

def preview_adaptations():
    """Aperçu rapide des types d'adaptations"""
    
    print("\n👀 Types de contenu adapté qui sera généré :")
    print("-" * 50)
    print("🔹 Introduction réécrite en langage simple")
    print("🔹 Sections du cours reformulées")
    print("🔹 Exercices réécrits avec consignes claires")
    print("🔹 Instructions simplifiées étape par étape")
    print("🔹 Guide de présentation visuelle")
    print("🔹 Exemple d'évaluation adaptée")

if __name__ == "__main__":
    preview_adaptations()
    test_single_course() 