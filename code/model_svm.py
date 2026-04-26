import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

print("1. Chargement des données...")
# Загружаем вашу таблицу (имена колонок теперь в нижнем регистре)
df = pd.read_csv('subtitles_dataset.csv')

# Убедимся, что нет пустых значений в текстах
df = df.dropna(subset=['texte', 'decennie'])

print("2. Séparation Stratifiée (80% Train / 20% Test)...")
X = df['texte']
y = df['decennie']

# stratify=y гарантирует, что в 80% попадет равная пропорция фильмов из каждого десятилетия
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.20, 
    random_state=42, 
    stratify=y
)

print(f"Taille du jeu d'entraînement (Train) : {len(X_train)} films")
print(f"Taille du jeu de test (Test) : {len(X_test)} films\n")

print("3. Vectorisation TF-IDF...")
# Превращаем текст в частотную матрицу. 
# max_features=5000 берет топ-5000 самых важных слов.
# stop_words='english' автоматически удаляет "the", "a", "is" и т.д.
vectoriseur = TfidfVectorizer(max_features=5000, stop_words='english')

X_train_tfidf = vectoriseur.fit_transform(X_train)
X_test_tfidf = vectoriseur.transform(X_test) # Важно: для Test мы делаем только transform()!

print("4. Entraînement du modèle SVM...")
modele_svm = LinearSVC(random_state=42)
modele_svm.fit(X_train_tfidf, y_train)

print("5. Prédiction et Évaluation...")
y_pred = modele_svm.predict(X_test_tfidf)

# Выводим финальный отчет о точности
print("\n=== RÉSULTATS DU MODÈLE SVM ===")
precision_globale = accuracy_score(y_test, y_pred)
print(f"Accuracy (Précision globale) : {precision_globale * 100:.2f}%\n")

print("Rapport détaillé par décennie (Classification Report) :")
print(classification_report(y_test, y_pred))