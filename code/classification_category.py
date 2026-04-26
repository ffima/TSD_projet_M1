"""
Script de classification de textes.
Ce script utilise scikit-learn pour la vectorisation (TF-IDF) et teste 
trois algorithmes de classification (Naïf Bayésien, SVM, Arbre de Décision).

Prérequis : pip install scikit-learn

MODE D'EMPLOI :
Exécution par défaut : python classification.py
Exécution avec arguments : python classification.py <chemin_train> <chemin_test>
"""

import sys
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score

def charger_donnees(chemin_dossier):
    """
    Parcourt le dossier (train ou test) contenant les dossiers de décennies.
    Lit le contenu de chaque fichier .txt et extrait l'étiquette (oscar ou blockbuster)
    à partir du nom du fichier.
    """
    textes = []
    etiquettes = []
    chemin_base = Path(chemin_dossier)
    
    if not chemin_base.exists():
        print(f"Erreur : Le dossier {chemin_dossier} n'existe pas.")
        return textes, etiquettes

    # Parcours des dossiers par décennie (1950s, 1960s, etc.)
    for dossier_decennie in chemin_base.iterdir():
        if not dossier_decennie.is_dir():
            continue
            
        # Parcours des fichiers texte
        for fichier_txt in dossier_decennie.glob("*.txt"):
            nom_fichier = fichier_txt.name.lower()
            
            # Détermination de la classe basée sur le nom du fichier
            if "oscar" in nom_fichier:
                classe = "oscar"
            elif "blockbuster" in nom_fichier:
                classe = "blockbuster"
            else:
                continue # Ignore les fichiers sans étiquette claire
                
            # Lecture du contenu du fichier
            try:
                # Utilisation de utf-8 avec gestion des erreurs pour éviter les plantages
                contenu = fichier_txt.read_text(encoding="utf-8", errors="ignore")
                textes.append(contenu)
                etiquettes.append(classe)
            except Exception as e:
                print(f"Erreur lors de la lecture de {fichier_txt} : {e}")
                
    return textes, etiquettes

def main():
    # 1. Chargement des données
    if len(sys.argv) > 2:
        dossier_train = sys.argv[1]
        dossier_test = sys.argv[2]
    else:
        # Chemins par défaut (remonte d'un niveau depuis le dossier 'code')
        dossier_racine = Path(__file__).parent.parent
        dossier_train = dossier_racine / "dataset" / "train"
        dossier_test = dossier_racine / "dataset" / "test"
    
    print("=== Chargement des données ===")
    print(f"Lecture des données d'entraînement depuis : {dossier_train}...")
    X_train, y_train = charger_donnees(dossier_train)
    
    print(f"Lecture des données de test depuis : {dossier_test}...")
    X_test, y_test = charger_donnees(dossier_test)
    
    print(f"\nDocuments d'entraînement : {len(X_train)}")
    print(f"Documents de test : {len(X_test)}")
    
    if len(X_train) == 0 or len(X_test) == 0:
        print("Erreur : Données insuffisantes pour l'entraînement ou le test. Vérifiez la structure des dossiers.")
        return

    # 2. Vectorisation (TF-IDF)
    print("\n=== Vectorisation des textes (TF-IDF) ===")
    vectoriseur = TfidfVectorizer(
        lowercase=True,
        max_df=0.95, # Ignore les mots présents dans plus de 95% des documents
        min_df=2     # Ignore les mots présents dans au moins 2 documents
    )
    
    print("Vectorisation du corpus d'entraînement...")
    X_train_vec = vectoriseur.fit_transform(X_train)
    
    print("Vectorisation du corpus de test...")
    X_test_vec = vectoriseur.transform(X_test)
    
    print(f"Taille du vocabulaire extrait : {X_train_vec.shape[1]} mots.")

    # 3. Modèle d'apprentissage automatique
    '''
    Modèles utilisés lors de la première execution du script
    modeles = {
        "Naïf Bayésien (MultinomialNB)": MultinomialNB(),
        "Machine à Vecteurs de Support (LinearSVC)": LinearSVC(random_state=42, dual=False),
        "Arbre de Décision (J48 / DecisionTreeClassifier)": DecisionTreeClassifier(random_state=42)
    }
    '''
    modeles = {
        # Naïf Bayésien standard, mais on désactive la prise en compte du déséquilibre des classes (fit_prior=False)
        "Naïf Bayésien (MultinomialNB corrigé)": MultinomialNB(fit_prior=False),
        # Version de Bayes conçue spécialement pour les corpus de textes déséquilibrés
        "Naïf Bayésien (ComplementNB)": ComplementNB(),
        "Machine à Vecteurs de Support (LinearSVC)": LinearSVC(random_state=42, dual=False),
        "Arbre de Décision (J48 / DecisionTreeClassifier)": DecisionTreeClassifier(random_state=42)
    }

    # 4. Entraînement et évaluation
    print("\n=== Évaluation des Modèles ===")
    
    for nom_modele, modele in modeles.items():
        print(f"\n--- {nom_modele} ---")
        
        # Entraînement
        modele.fit(X_train_vec, y_train)
        
        # Prédiction
        predictions = modele.predict(X_test_vec)
        
        # Évaluation
        precision_globale = accuracy_score(y_test, predictions)
        print(f"Précision globale (Accuracy) : {precision_globale:.4f}")
        
        print("\nRapport de classification :")
        print(classification_report(y_test, predictions))

if __name__ == "__main__":
    main()