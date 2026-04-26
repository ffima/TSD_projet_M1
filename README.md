# Projet de cours — Traitement statistique des données (Master TAL)
## Classification de sous-titres de films par ère cinématographique

Ce dépôt contient le code source et les scripts développés dans le cadre du projet de Master TAL (Plurital, Semestre 2).

L'objectif est d'entraîner et de comparer les performances de différents algorithmes de classification par apprentissage automatique sur un corpus de sous-titres de films des années 1950 à 2024. La tâche consiste à prédire à quelle **ère cinématographique** appartient un film en se basant uniquement sur les dialogues de son script.

Les trois ères définies sont :

| Ère | Années couvertes |
|---|---|
| `1950-1975` | 1950 – 1975 |
| `1976-1999` | 1976 – 1999 |
| `2000-2024` | 2000 – 2024 |

---

## Structure du projet

```
projet/
├── code/
│   ├── process.py               # Étape 1 : réorganisation des .srt par ère
│   ├── srt_to_txt.py            # Étape 2 : conversion .srt → .txt nettoyé
│   ├── split.py                 # Étape 3 : séparation train / test
│   ├── classification.py        # Étape 4 : vectorisation, entraînement, évaluation
│   └── count_docs.py            # Utilitaire : statistiques de distribution
├── data/
│   ├── srts/                    # Fichiers .srt bruts (source, non modifiée)
│   │   ├── Blockbusters/
│   │   │   ├── 1950/
│   │   │   └── ...
│   │   └── Oscars/
│   │       ├── 1950/
│   │       └── ...
│   ├── raw/                     # Fichiers .srt réorganisés par ère
│   │   ├── 1950-1975/
│   │   ├── 1976-1999/
│   │   └── 2000-2024/
│   └── processed/               # Fichiers .txt nettoyés, même structure
│       ├── 1950-1975/
│       ├── 1976-1999/
│       └── 2000-2024/
├── dataset/
│   ├── train/                   # 80 % des données, organisées par ère
│   └── test/                    # 20 % des données, organisées par ère
└── resultats/                   # Fichiers de résultats horodatés (.txt)
```

---

## Pipeline de traitement

```
data/srts/      →  process.py     →  data/raw/
data/raw/       →  srt_to_txt.py  →  data/processed/
data/processed/ →  split.py       →  dataset/train/  +  dataset/test/
dataset/        →  classification.py  →  resultats/
```

### `process.py` — Réorganisation par ère

Lit les fichiers `.srt` bruts depuis `data/srts/` (structuré par catégorie puis par année) et les recopie dans `data/raw/` en les regroupant selon leur ère cinématographique. La catégorie est intégrée dans le nom du fichier.

Exemple : `data/srts/Blockbusters/1968/2001.srt` → `data/raw/1950-1975/2001 (Blockbusters).srt`

```bash
python process.py
# ou
python process.py ../data/srts ../data/raw
```

### `srt_to_txt.py` — Nettoyage des sous-titres

Parcourt `data/raw/` et convertit chaque fichier `.srt` en `.txt` pur en supprimant les horodatages, les numéros de séquence et les balises HTML. La structure par ères est préservée dans `data/processed/`.

```bash
python srt_to_txt.py
# ou
python srt_to_txt.py ../data/raw ../data/processed
```

### `split.py` — Séparation train / test

Divise le corpus de manière **stratifiée par catégorie** (oscar / blockbuster) : 80 % des fichiers vont dans `dataset/train/`, 20 % dans `dataset/test/`. La structure par ères est préservée dans les deux dossiers de sortie. La graine `random.seed(42)` garantit la reproductibilité.

```bash
python split.py
# ou
python split.py ../data/processed ../dataset/train ../dataset/test 0.8
```

### `classification.py` — Classification et évaluation

Script principal. Il charge les données, les vectorise avec TF-IDF selon trois configurations, entraîne plusieurs modèles et sauvegarde automatiquement tous les résultats dans `resultats/` sous la forme `resultats_eras{YYYYMMDD_HHMMSS}.txt`.

```bash
python classification.py
# ou
python classification.py ../dataset/train ../dataset/test
```

**Trois vectorisations comparées :**

| Configuration | Paramètres clés |
|---|---|
| TF-IDF baseline | unigrammes, `max_df=0.95`, `min_df=2` |
| TF-IDF amélioré | unigrammes + bigrammes, stop words anglais, `sublinear_tf=True` |
| TF-IDF caractères | n-grammes de caractères (3–5), `sublinear_tf=True` |

**Cinq modèles évalués :**

| Modèle | Notes |
|---|---|
| **SVM — LinearSVC** (+ GridSearchCV sur `C`) | Meilleur modèle sur nos données |
| **Naïf Bayésien — ComplementNB** | Adapté aux corpus déséquilibrés |
| **Régression Logistique** | Bonne baseline linéaire |
| **Arbre de Décision (J48)** | Interprétable, moins performant sur texte |
| **Random Forest** | Modèle ensembliste |

### `count_docs.py` — Statistiques de distribution

Affiche le nombre de documents `.txt` par dossier (ère) dans un répertoire donné.

```bash
python count_docs.py ../dataset/train
python count_docs.py ../dataset/test
```

---

## Prérequis

```bash
pip install scikit-learn pandas
```

Python 3.10 ou supérieur recommandé (utilisation de `match` implicite et annotations de type modernes).

---

## Reproductibilité

- La graine aléatoire est fixée à `42` dans `split.py` pour garantir une séparation train/test identique à chaque exécution.
- Tous les modèles utilisent `random_state=42`.
- Chaque exécution de `classification.py` génère un fichier de résultats horodaté dans `resultats/`, ce qui permet de comparer les expériences sans écraser les résultats précédents.