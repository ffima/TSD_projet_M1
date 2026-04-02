import shutil
from pathlib import Path

def organize_dataset():
    base_path = Path(__file__).parent
    
    src_path = base_path / "data" / "srts"
    dest_path = base_path / "data" / "raw"

    if not src_path.exists():
        print(f"Erreur: Dossier source '{src_path}' non trouvé! Vérifiez la structure.")
        return

    print(f"Recherche de fichiers dans: {src_path}")
    print(f"Création de nouveaux dossiers dans: {dest_path}\n")

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

            # 3. Calcul de la décennie (par exemple, 1954 // 10 * 10 = 1950)
            decade = (year // 10) * 10
            decade_folder_name = f"{decade}s"
            
            # Création du dossier décennie (par exemple, data/raw/1950s)
            target_decade_dir = dest_path / decade_folder_name
            target_decade_dir.mkdir(parents=True, exist_ok=True)

            # 4. Traitement de chaque fichier .srt
            for file_path in year_dir.glob("*.srt"):
                # Formatter un nouveau nom: "Nom original (Catégorie).srt"
                new_filename = f"{file_path.stem} ({category_name}){file_path.suffix}"
                target_file_path = target_decade_dir / new_filename

                # Copier le fichier (pour ne pas détruire les sources dans srts)
                shutil.copy2(file_path, target_file_path)
                
                print(f"[{decade_folder_name}] {new_filename}")
                files_processed += 1

    print(f"\nFini! Fichiers traités: {files_processed}")

if __name__ == "__main__":
    organize_dataset()