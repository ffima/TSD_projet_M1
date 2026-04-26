"""
MODE D'EMPLOI :
1. Placez ce script dans le dossier 'code/'.
2. Exécution avec valeurs par défaut : python process.py
3. Exécution avec chemins personnalisés : python process.py <dossier_source> <dossier_destination>
   Exemple : python process.py ../data/srts ../data/raw
"""

import shutil
from pathlib import Path
import sys

def organize_dataset(src_dir, dest_dir):
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)

    if not src_path.exists():
        print(f"Erreur : Dossier source '{src_path}' non trouvé.")
        return

    print(f"Organisation des fichiers de {src_path} vers {dest_path}...")
    files_processed = 0

    # 1. Parcours des dossiers de catégories (Blockbusters et Oscars)
    for category_dir in src_path.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name

        # 2. Parcours des dossiers d'années (1950, 1951...)
        for year_dir in category_dir.iterdir():
            if not year_dir.is_dir():
                continue

            try:
                year = int(year_dir.name)
            except ValueError:
                continue

        # 3. Définition de l'ère en fonction de l'année
            if 1950 <= year <= 1975:
                era_folder_name = "1950-1975"
            elif 1976 <= year <= 1999:
                era_folder_name = "1976-1999"
            elif 2000 <= year <= 2024:
                era_folder_name = "2000-2024"
            else:
                continue
            
            # Création du dossier de l'ère (par exemple, data/raw/1950-1975)
            target_era_dir = dest_path / era_folder_name
            target_era_dir.mkdir(parents=True, exist_ok=True)

            # 4. Traitement de chaque fichier .srt
            for file_path in year_dir.glob("*.srt"):
                # Formater un nouveau nom : "Nom original (Catégorie).srt"
                new_filename = f"{file_path.stem} ({category_name}){file_path.suffix}"
                target_file_path = target_era_dir / new_filename

                # Copier le fichier
                shutil.copy2(file_path, target_file_path)
                
                print(f"[{era_folder_name}] {new_filename}")
                files_processed += 1

    print(f"\nTerminé ! Fichiers traités : {files_processed}")

if __name__ == "__main__":
    # Récupération des arguments via sys.argv ou utilisation des valeurs par défaut
    src_directory = sys.argv[1] if len(sys.argv) > 1 else "../data/srts"
    dest_directory = sys.argv[2] if len(sys.argv) > 2 else "../data/raw"
    
    organize_dataset(src_directory, dest_directory)