# Projet de cours Traitement statistique des données de Master TAL : Classification de textes (Oscars vs Blockbusters)

Ce dépôt contient le code source et les scripts développés dans le cadre de ce projet.

L'objectif de ce projet est d'entraîner et de comparer les performances de différents algorithmes de classification par apprentissage automatique (*Machine Learning*) sur un corpus de sous-titres de films des années 1950 à 2020. La tâche consiste à prédire si un film appartient à la catégorie **"Oscar"** ou **"Blockbuster"** en se basant uniquement sur les dialogues de son script.

## Pipeline de Traitement et Scripts

Le projet propose une chaîne de traitement (pipeline) complète de bout en bout, de la préparation des données jusqu'à l'évaluation des modèles :

* **`process.py`** : Réorganise les fichiers `.srt` bruts en les regroupant par décennies (1950s, 1960s, etc.) et ajoute la catégorie dans le nom du fichier.
* **`srt_to_txt.py`** : Nettoie les sous-titres en supprimant les horodatages (timestamps), les numéros de ligne et les métadonnées pour extraire le texte pur au format `.txt`.
* **`split.py`** : Divise le corpus de manière stratifiée en ensembles d'entraînement (`train`, 80%) et de test (`test`, 20%), tout en préservant l'équilibre des classes et la structure par décennies. Un *seed* est fixé pour garantir la reproductibilité.
* **`classification.py`** : Script principal qui utilise `scikit-learn` pour vectoriser les textes (TF-IDF) et évaluer différents modèles d'apprentissage automatique.
* **`count_docs.py`** : Utilitaire permettant d'obtenir rapidement les statistiques de distribution des documents dans les dossiers.

## Algorithmes de Classification Évalués

Au lieu d'utiliser le format ARFF et l'outil Weka, ce projet utilise la bibliothèque **scikit-learn** en Python. Les modèles suivants ont été comparés :
1. **Machine à Vecteurs de Support (LinearSVC)** *(Meilleur modèle pour nos données textuelles clairsemées)*
2. **Naïf Bayésien (MultinomialNB & ComplementNB)** *(Ajustés pour limiter le biais des classes déséquilibrées)*
3. **Arbre de Décision (DecisionTreeClassifier / J48)**

## Prérequis et Utilisation

**Installation :**
Assurez-vous d'avoir Python installé ainsi que la bibliothèque `scikit-learn`.
```bash
pip install scikit-learn