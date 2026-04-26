"""
MODE D'EMPLOI :
    python classification_era_v2.py
    python classification_era_v2.py <chemin_train> <chemin_test>
"""

import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


STOP_WORDS = "english"


# ---------------------------------------------------------------------------
# Tee : écrit simultanément dans la console ET dans un fichier
# ---------------------------------------------------------------------------

class Tee:
    """Duplique sys.stdout vers un fichier ouvert en écriture."""
    def __init__(self, fichier):
        self._fichier = fichier
        self._stdout  = sys.stdout

    def write(self, data):
        self._stdout.write(data)
        self._fichier.write(data)

    def flush(self):
        self._stdout.flush()
        self._fichier.flush()


# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------

def charger_donnees(chemin_dossier):
    textes, etiquettes = [], []
    chemin_base = Path(chemin_dossier)

    if not chemin_base.exists():
        print(f"Erreur : dossier introuvable -> {chemin_dossier}")
        return textes, etiquettes

    for dossier_ere in sorted(chemin_base.iterdir()):
        if not dossier_ere.is_dir():
            continue
        classe = dossier_ere.name
        for fichier in dossier_ere.glob("*.txt"):
            try:
                textes.append(fichier.read_text(encoding="utf-8", errors="ignore"))
                etiquettes.append(classe)
            except Exception as e:
                print(f"Erreur lecture {fichier} : {e}")

    return textes, etiquettes


# ---------------------------------------------------------------------------
# Matrice de confusion
# ---------------------------------------------------------------------------

def afficher_confusion(y_test, predictions, classes):
    cm = confusion_matrix(y_test, predictions, labels=classes)
    col_w = max(len(c) for c in classes) + 2
    header = " " * col_w + "".join(c.ljust(col_w) for c in classes)
    print("  Matrice de confusion :")
    print("  " + header)
    for i, row in enumerate(cm):
        print("  " + classes[i].ljust(col_w) + "".join(str(v).ljust(col_w) for v in row))


# ---------------------------------------------------------------------------
# Coeur du script
# ---------------------------------------------------------------------------

def run(dossier_train, dossier_test):
    print("=" * 65)
    print("  CLASSIFICATION PAR ERES - VERSION AMELIOREE")
    print("=" * 65)
    print(f"\nTrain : {dossier_train}")
    X_train, y_train = charger_donnees(dossier_train)
    print(f"Test  : {dossier_test}")
    X_test, y_test = charger_donnees(dossier_test)

    print(f"\nDocuments d'entrainement : {len(X_train)}")
    print(f"Documents de test        : {len(X_test)}")
    print("\nRepartition train :", dict(sorted(Counter(y_train).items())))
    print("Repartition test  :", dict(sorted(Counter(y_test).items())))

    if not X_train or not X_test:
        print("\nErreur : donnees insuffisantes.")
        return

    classes = sorted(set(y_train))

    # -------------------------------------------------------------------
    # Trois vectorisations a comparer
    # -------------------------------------------------------------------
    vectorisations = {
        "TF-IDF baseline": TfidfVectorizer(
            lowercase=True,
            max_df=0.95,
            min_df=2,
        ),
        "TF-IDF ameliore (stop words + bigrams + sublinear)": TfidfVectorizer(
            lowercase=True,
            stop_words=STOP_WORDS,
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_df=0.90,
            min_df=3,
            max_features=80_000,
        ),
        "TF-IDF caracteres (3-5-grammes)": TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            sublinear_tf=True,
            max_df=0.95,
            min_df=3,
            max_features=60_000,
        ),
    }

    # -------------------------------------------------------------------
    # Modeles
    # -------------------------------------------------------------------
    svm_grid = GridSearchCV(
        LinearSVC(random_state=42, dual=False, max_iter=2000),
        param_grid={"C": [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]},
        cv=StratifiedKFold(n_splits=5),
        scoring="accuracy",
        n_jobs=-1,
    )

    modeles_base = {
        "Naif Bayesien (ComplementNB)": ComplementNB(),
        "SVM - LinearSVC (C=1)":        LinearSVC(random_state=42, dual=False),
        "Regression Logistique":        LogisticRegression(
                                            max_iter=1000, random_state=42,
                                            solver="lbfgs"),
        "Random Forest":                RandomForestClassifier(
                                            n_estimators=300, random_state=42, n_jobs=-1),
    }

    best_acc   = 0.0
    best_label = ""

    # -------------------------------------------------------------------
    # Boucle vectorisation x modele
    # -------------------------------------------------------------------
    for vec_name, vectoriseur in vectorisations.items():
        print(f"\n{'=' * 65}")
        print(f"  VECTORISATION : {vec_name}")
        print(f"{'=' * 65}")

        X_train_vec = vectoriseur.fit_transform(X_train)
        X_test_vec  = vectoriseur.transform(X_test)
        print(f"  Dimensions : {X_train_vec.shape[1]} termes\n")

        for nom, modele in modeles_base.items():
            # ComplementNB ne supporte pas les valeurs negatives -> skip char n-grams
            if "Bayesien" in nom and "caracteres" in vec_name:
                continue

            print(f"  > {nom}")
            modele.fit(X_train_vec, y_train)
            preds = modele.predict(X_test_vec)
            acc   = accuracy_score(y_test, preds)
            print(f"    Accuracy : {acc:.4f}  ({acc*100:.2f} %)")
            print(classification_report(y_test, preds, target_names=classes,
                                        zero_division=0))
            afficher_confusion(y_test, preds, classes)
            print()

            label = f"{vec_name}  +  {nom}"
            if acc > best_acc:
                best_acc   = acc
                best_label = label

    # -------------------------------------------------------------------
    # SVM + GridSearchCV (vectorisation amelioree)
    # -------------------------------------------------------------------
    print(f"\n{'=' * 65}")
    print("  OPTIMISATION : SVM + GridSearchCV (vectorisation amelioree)")
    print(f"{'=' * 65}")

    vec_opt = TfidfVectorizer(
        lowercase=True, stop_words=STOP_WORDS,
        ngram_range=(1, 2), sublinear_tf=True,
        max_df=0.90, min_df=3, max_features=80_000,
    )
    X_train_opt = vec_opt.fit_transform(X_train)
    X_test_opt  = vec_opt.transform(X_test)

    print("  Recherche du meilleur C sur 5-fold CV...")
    svm_grid.fit(X_train_opt, y_train)
    print(f"  Meilleur C : {svm_grid.best_params_['C']}  "
          f"(CV accuracy : {svm_grid.best_score_:.4f})")

    preds_grid = svm_grid.predict(X_test_opt)
    acc_grid   = accuracy_score(y_test, preds_grid)
    print(f"  Accuracy test : {acc_grid:.4f}  ({acc_grid*100:.2f} %)")
    print(classification_report(y_test, preds_grid, target_names=classes, zero_division=0))
    afficher_confusion(y_test, preds_grid, classes)

    if acc_grid > best_acc:
        best_acc   = acc_grid
        best_label = "TF-IDF ameliore  +  SVM GridSearch"

    # -------------------------------------------------------------------
    # Resume final
    # -------------------------------------------------------------------
    print(f"\n{'=' * 65}")
    print("  RESUME")
    print(f"{'=' * 65}")
    print(f"  Meilleure configuration : {best_label}")
    print(f"  Accuracy                : {best_acc:.4f}  ({best_acc*100:.2f} %)")
    print()


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def main():
    # Chemins train / test
    if len(sys.argv) > 2:
        dossier_train = Path(sys.argv[1])
        dossier_test  = Path(sys.argv[2])
    else:
        racine        = Path(__file__).parent.parent
        dossier_train = racine / "dataset" / "train"
        dossier_test  = racine / "dataset" / "test"

    # Dossier de sauvegarde des resultats
    dossier_resultats = Path(__file__).parent.parent / "resultats"
    dossier_resultats.mkdir(parents=True, exist_ok=True)

    horodatage  = datetime.now().strftime("%Y%m%d_%H%M%S")
    fichier_log = dossier_resultats / f"resultats_eras{horodatage}.txt"

    # Lancement avec redirection stdout -> console + fichier
    with open(fichier_log, "w", encoding="utf-8") as f_log:
        stdout_original = sys.stdout
        sys.stdout = Tee(f_log)

        run(dossier_train, dossier_test)

        sys.stdout = stdout_original

    print(f"\nResultats sauvegardes -> {fichier_log}")


if __name__ == "__main__":
    main()