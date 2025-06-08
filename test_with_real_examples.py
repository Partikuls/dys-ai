#!/usr/bin/env python3
"""
Test d'Amélioration avec Exemples Réels
Compare les adaptations avec et sans exemples réels
"""

from course_adapter import CourseAdapter
from real_examples_provider import RealExamplesProvider

def test_adaptation_with_real_examples():
    """Test l'adaptation avec les exemples réels"""
    
    print("🧪 Test d'Adaptation avec Exemples Réels")
    print("=" * 55)
    
    # Vérifier si les exemples sont disponibles
    provider = RealExamplesProvider()
    
    if not provider.has_examples():
        print("❌ Aucun exemple réel trouvé.")
        print("   Exécutez d'abord : python real_examples_extractor.py")
        return
    
    # Afficher les statistiques des exemples
    stats = provider.get_stats()
    print(f"📚 Exemples disponibles : {stats['total_examples']}")
    print(f"📖 Matières : {', '.join(stats['subjects'])}")
    print(f"📁 Sources : {len(stats['sources'])} cours")
    
    # Test avec le cours existant
    adapter = CourseAdapter()
    course_file = "Civilsetmilitaires1GM.pdf"
    course_path = f"pdf-cours/{course_file}"
    
    try:
        print(f"\n🎯 Test avec : {course_file}")
        
        # Extraire le contenu
        print("🔍 Extraction du contenu...")
        course_content = adapter.extract_course_content(course_path)
        
        if not course_content['sections']:
            print("⚠️  Aucune section détectée dans le cours")
            return
        
        print(f"   ✅ {len(course_content['sections'])} sections trouvées")
        
        # Test avec les exemples réels (limiter à 1 section pour économiser les tokens)
        print("\n🚀 Génération d'adaptation avec exemples réels...")
        
        # Prendre seulement la première section pour le test
        test_section = course_content['sections'][0]
        
        # Adapter avec exemples réels
        from real_examples_provider import get_real_example_for_prompt
        
        real_example = get_real_example_for_prompt("section", test_section['content'][:200], "Histoire")
        
        section_query_with_examples = f"""{real_example}

TITRE ORIGINAL: {test_section['title']}
CONTENU ORIGINAL: {test_section['content'][:500]}...

INSTRUCTIONS: Réécris cette section avec :
- Phrases courtes et simples
- Vocabulaire accessible 
- Structure claire avec des sous-titres
- Exemples concrets
- Points clés mis en évidence

CRÉE LE TEXTE ADAPTÉ DE LA SECTION:"""
        
        response_with_examples = adapter.rag_system.query(section_query_with_examples)
        
        print("✅ Adaptation générée avec exemples réels")
        
        # Afficher les résultats
        print("\n" + "="*60)
        print("RÉSULTATS DE L'ADAPTATION")
        print("="*60)
        
        print(f"\n📖 SECTION ORIGINALE :")
        print(f"Titre : {test_section['title']}")
        print(f"Aperçu : {test_section['content'][:200]}...")
        
        print(f"\n✨ SECTION ADAPTÉE (avec exemples réels) :")
        print(response_with_examples['answer'][:500] + "..." if len(response_with_examples['answer']) > 500 else response_with_examples['answer'])
        
        print(f"\n📊 SOURCES UTILISÉES :")
        if response_with_examples['sources']:
            for i, source in enumerate(response_with_examples['sources'][:2], 1):
                print(f"   {i}. {source['source']} par {source['author']}")
        else:
            print("   Aucune source trouvée")
        
        print("\n" + "="*60)
        
        # Afficher un exemple réel utilisé
        if provider.has_examples():
            print("\n📚 EXEMPLE RÉEL UTILISÉ COMME MODÈLE :")
            example = provider.get_section_example("Histoire")
            lines = example.split('\n')
            for line in lines[:10]:  # Afficher les 10 premières lignes
                if line.strip():
                    print(f"   {line}")
            print("   ...")
        
        print("\n🎉 Test terminé avec succès !")
        print("\n💡 L'adaptation utilise maintenant de vrais exemples d'adaptation")
        print("   tirés de vos cours avant/après pour améliorer la qualité.")
        
    except FileNotFoundError:
        print(f"❌ Fichier {course_path} non trouvé")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

def preview_real_examples():
    """Affiche un aperçu des exemples réels disponibles"""
    provider = RealExamplesProvider()
    provider.preview_examples()

if __name__ == "__main__":
    print("🔍 Aperçu des exemples réels disponibles :")
    preview_real_examples()
    
    print("\n" + "="*60)
    test_adaptation_with_real_examples() 