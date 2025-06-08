# Guide d'Adaptation de Cours pour Dyslexiques 📚

Ce guide explique comment utiliser le système d'adaptation automatique de cours pour les élèves dyslexiques.

## 🎯 Objectif

Transformer automatiquement vos cours existants (PDF) en versions adaptées aux élèves dyslexiques en utilisant l'intelligence artificielle et la recherche académique.

## 📁 Structure des Dossiers

```
dys-ai/
├── pdf-cours/              # 📥 Vos cours originaux (PDF)
│   └── Civilsetmilitaires1GM.pdf
├── cours-adaptes/          # 📤 Cours adaptés générés
│   ├── Civilsetmilitaires1GM_adapte_dyslexie.md
│   └── Civilsetmilitaires1GM_adapte_dyslexie.json
├── course_adapter.py       # 🔧 Script principal d'adaptation
└── test_course_adaptation.py # 🧪 Script de test
```

## 🚀 Utilisation Rapide

### 1. Tester avec un cours spécifique

```bash
# Test avec votre cours "Civilsetmilitaires1GM.pdf"
python test_course_adaptation.py
```

### 2. Adapter tous les cours

```bash
# Traiter tous les PDFs dans pdf-cours/
python course_adapter.py
```

### 3. Adapter un cours spécifique

```bash
# Traiter uniquement un fichier
python course_adapter.py --course Civilsetmilitaires1GM.pdf
```

### 4. Choisir le format de sortie

```bash
# Format Markdown (par défaut, facile à lire)
python course_adapter.py --format markdown

# Format JSON (pour analyse programmée)
python course_adapter.py --format json

# Format texte simple
python course_adapter.py --format text
```

## 🔍 Ce que fait le système

### 📖 Analyse du Cours
- **Extraction automatique** des sections, exercices, consignes
- **Détection de la structure** (titres, sous-parties)
- **Identification des éléments pédagogiques**

### 🤖 Génération de Contenu Adapté

Le système utilise votre base de connaissances sur la dyslexie pour CRÉER directement :

1. **Introduction Réécrite**
   - Texte d'introduction simplifié et accessible
   - Langage adapté aux dyslexiques
   - Structure claire et motivante

2. **Sections du Cours Reformulées**
   - Contenu entièrement réécrit avec vocabulaire simple
   - Phrases courtes (15-20 mots maximum)
   - Structure avec titres clairs et exemples concrets

3. **Exercices Complètement Réécrits**
   - Consignes étape par étape
   - Instructions simples et directes
   - Support visuel et structuré

4. **Instructions Reformulées**
   - Langage précis et sans ambiguïté
   - Une instruction par phrase
   - Ordre logique des étapes

5. **Guide de Présentation Spécifique**
   - Instructions concrètes de mise en forme
   - Recommandations visuelles adaptées
   - Format optimisé pour dyslexiques

6. **Exemple d'Évaluation Concrète**
   - Modèle d'évaluation entièrement adapté
   - Exercices d'évaluation réécrits
   - Barème et critères ajustés

## 📋 Exemple de Résultat

Après traitement, vous obtenez un cours complet adapté comme :

```markdown
# Civilsetmilitaires1GM - Version Adaptée aux Dyslexiques

## 📚 Introduction
La Première Guerre mondiale est un conflit important. 
Elle a eu lieu de 1914 à 1918. Cette guerre a changé l'Europe.

Dans ce cours, nous allons étudier :
- Les causes de la guerre
- Les pays qui ont participé  
- Les conséquences importantes

## 📖 Contenu du Cours

### 1. Les causes de la guerre
La guerre a commencé à cause de plusieurs problèmes.

**Les alliances :**
- La France, la Russie et l'Angleterre étaient alliées
- L'Allemagne et l'Autriche étaient alliées aussi
- Ces deux groupes ne s'aimaient pas

**L'événement déclencheur :**
Le 28 juin 1914, un prince autrichien est tué.
Cet événement déclenche la guerre.

## 🎯 Exercices

### Exercice 1
**Complète la frise chronologique :**

1. Trouve les dates importantes
2. Place-les dans l'ordre sur la ligne
3. Écris un mot pour expliquer chaque date

Aide : Utilise tes notes et le cours
```

## ⚙️ Personnalisation

### Modifier les Paramètres

Dans `course_adapter.py`, vous pouvez ajuster :

```python
# Nombre de sections analysées (par défaut : 5)
course_content["sections"][:5]

# Nombre d'exercices adaptés (par défaut : 3)
course_content["exercises"][:3]

# Répertoires source et destination
self.courses_dir = "pdf-cours"
self.output_dir = "cours-adaptes"
```

### Ajouter des Mots-clés

Pour améliorer la détection, modifiez les listes :

```python
exercise_keywords = ['exercice', 'activité', 'travail', 'devoir', 'question']
instruction_keywords = ['consigne', 'instruction', 'lisez', 'écrivez']
```

## 🔧 Dépannage

### Problème : "Aucun fichier PDF trouvé"
- Vérifiez que vos PDFs sont dans le dossier `pdf-cours/`
- Les fichiers doivent avoir l'extension `.pdf`

### Problème : "Erreur de connexion API"
- Vérifiez votre clé OpenAI dans les variables d'environnement
- Vérifiez votre crédit API OpenAI

### Problème : "Aucune section détectée"
- Le PDF peut être scanné (image) sans texte extractible
- Essayez avec un PDF contenant du texte sélectionnable

### Problème : "Adaptations peu pertinentes"
- Assurez-vous d'avoir bien configuré la base de connaissances dyslexie
- Vérifiez que `python main.py setup` a été exécuté

## 💡 Conseils d'Utilisation

### Pour de Meilleurs Résultats
1. **PDFs textuels** : Utilisez des PDFs avec du texte sélectionnable
2. **Structure claire** : Les cours avec titres et sections donnent de meilleurs résultats
3. **Base de connaissances** : Plus votre base de recherche dyslexie est riche, meilleures sont les adaptations

### Workflow Recommandé
1. **Configuration initiale** : `python main.py setup` (une seule fois)
2. **Test** : `python test_course_adaptation.py` 
3. **Adaptation en masse** : `python course_adapter.py`
4. **Révision manuelle** : Vérifiez et ajustez les adaptations générées

## 📞 Support

En cas de problème :
1. Vérifiez ce guide
2. Testez avec `python test_course_adaptation.py`
3. Vérifiez les logs d'erreur pour diagnostiquer
4. Assurez-vous que toutes les dépendances sont installées

---

*Ce système utilise l'IA pour proposer des adaptations basées sur la recherche académique. Les suggestions doivent être révisées par un professionnel de l'éducation avant utilisation en classe.* 