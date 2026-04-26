"""
MODE D'EMPLOI : python count_docs.py ../dataset/train
"""

import os
from collections import defaultdict
import sys

# Vérification des arguments
if len(sys.argv) < 2:
    print("Erreur : Veuillez spécifier le chemin du dossier.")
    print("Exemple : python count_docs.py ../dataset/test")
    sys.exit(1)

# Chemin de base vers le dossier cible
base_path = sys.argv[1] 

# Dictionnaire pour stocker le nombre de fichiers
counts = defaultdict(int)

# Parcours de chaque dossier de décennie
for decade_folder in os.listdir(base_path):
    folder_path = os.path.join(base_path, decade_folder)
    
    # Vérifie s'il s'agit bien d'un dossier
    if os.path.isdir(folder_path):
        # Liste tous les fichiers .txt dans ce dossier
        txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        counts[decade_folder] = len(txt_files)
        print(f"{decade_folder} : {len(txt_files)} documents")

print(f"\nTotal : {sum(counts.values())} documents")