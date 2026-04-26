"""
MODE D'EMPLOI :
1. Exécution par défaut : python split.py
2. Exécution personnalisée : python split.py <source> <train_dest> <test_dest> <ratio>
   Exemple : python split.py ../data/processed ../dataset/train ../dataset/test 0.8
"""

import shutil
import random
import sys
from pathlib import Path

def split_data(source_dir, train_dir, test_dir, split_ratio=0.8):
    """
    Sépare les fichiers texte en ensembles d'entraînement (train) et de test
    tout en préservant la structure des dossiers et la stratification.
    """
    source_path = Path(source_dir)
    train_path = Path(train_dir)
    test_path = Path(test_dir)

    # Création des répertoires de base s'ils n'existent pas
    train_path.mkdir(parents=True, exist_ok=True)
    test_path.mkdir(parents=True, exist_ok=True)

    # Parcours des dossiers par décennie
    for decade_folder in source_path.iterdir():
        if not decade_folder.is_dir():
            continue

        decade = decade_folder.name
        
        # Création des sous-dossiers correspondants dans train et test
        (train_path / decade).mkdir(parents=True, exist_ok=True)
        (test_path / decade).mkdir(parents=True, exist_ok=True)

        oscar_files = []
        blockbuster_files = []
        other_files = [] 

        # Tri des fichiers par catégorie selon leur nom
        for file_path in decade_folder.glob("*.txt"):
            filename_lower = file_path.name.lower()
            
            if "oscar" in filename_lower:
                oscar_files.append(file_path)
            elif "blockbuster" in filename_lower:
                blockbuster_files.append(file_path)
            else:
                other_files.append(file_path)

        def process_and_copy(file_list):
            if not file_list:
                return
            
            # Mélange aléatoire des fichiers
            random.shuffle(file_list)
            
            # Calcul de l'index de séparation
            split_idx = int(len(file_list) * split_ratio)
            
            train_files = file_list[:split_idx]
            test_files = file_list[split_idx:]
            
            # Copie des fichiers d'entraînement
            for f in train_files:
                shutil.copy2(f, train_path / decade / f.name)
                
            # Copie des fichiers de test
            for f in test_files:
                shutil.copy2(f, test_path / decade / f.name)

        # Application de la séparation pour chaque catégorie
        process_and_copy(oscar_files)
        process_and_copy(blockbuster_files)
        process_and_copy(other_files) 
        
        print(f"Dossier {decade} traité : "
              f"Fichiers Oscar : ({len(oscar_files)}), "
              f"Fichiers Blockbusters : ({len(blockbuster_files)}).")

if __name__ == "__main__":
    # Récupération des arguments via sys.argv
    source_dir = sys.argv[1] if len(sys.argv) > 1 else "../data/processed"
    train_dest = sys.argv[2] if len(sys.argv) > 2 else "../dataset/train"
    test_dest = sys.argv[3] if len(sys.argv) > 3 else "../dataset/test"
    split_ratio = float(sys.argv[4]) if len(sys.argv) > 4 else 0.8
    
    # Fixation de la graine (seed) pour la reproductibilité
    random.seed(42)

    print("Début du traitement...")
    split_data(source_dir, train_dest, test_dest, split_ratio)
    print("Traitement terminé.")