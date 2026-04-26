"""
source for the base of the script: https://gist.github.com/hshrews/e7b4f54edebf661c3dcde33d5d97c4cb.js

    About:
        Looks in the data/raw directory for any .srt (transcript) files to convert to a simple,
        single line of text with timestamps and numbered lines removed.
        Saves the processed .txt files to data/processed, preserving subdirectories.

    Assumptions:
        - lines beginning with lowercase letters or commas are part of the previous line
        - lines beginning with any other character are new lines

MODE D'EMPLOI :
1. Exécution avec valeurs par défaut : python srt_to_txt.py
2. Exécution personnalisée : python srt_to_txt.py <dossier_entree> <dossier_sortie>
"""

import os
import re
import sys 

def is_timestamp(l):
    return True if l[:2].isnumeric() and l[2] == ':' else False

def is_text_content(line):
    return True if re.search('[a-zA-Z]', line) else False

def has_no_text(line):
    if not len(line):
        return True
    if line.isnumeric():
        return True
    if is_timestamp(line):
        return True
    if line[0] == '(' and line[-1] == ')':
        return True
    if not is_text_content(line):
        return True
    return False

def filter_lines(lines):
    """ Remove timestamps, any lines without text, and line breaks """
    new_lines = []
    for line in lines[1:]:
        line = line.strip()
        if has_no_text(line):
            continue
        else:
            new_lines.append(line)

    joined_text = ' '.join(new_lines)
    
    clean_text = re.sub(r'<[^>]+>', '', joined_text)
    
    return clean_text.lower()

def file_srt_to_txt(file_path, target_dir, encoding):
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        data = filter_lines(f.readlines())
        
    new_file_name = os.path.join(target_dir, file_name[:-4]) + '.txt'
    
    with open(new_file_name, 'w', encoding='utf-8') as f:
        f.write(data)

def main():
    if len(sys.argv) > 2:
        raw_dir = sys.argv[1]
        processed_dir = sys.argv[2]
    else:
        # Chemins par défaut
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir) 
        
        raw_dir = os.path.join(base_dir, 'data', 'raw')
        processed_dir = os.path.join(base_dir, 'data', 'processed')

    if not os.path.isdir(raw_dir):
        print(f"Erreur : répertoire introuvable -> {raw_dir}")
        return

    encoding = 'utf-8'

    print(f"Analyse du répertoire : {raw_dir}")
    
    for root, _, files in os.walk(raw_dir):
        for file_name in files:
            if file_name.endswith(".srt"):
                file_path = os.path.join(root, file_name)
                
                rel_path = os.path.relpath(root, raw_dir)
                if rel_path == '.':
                    target_dir = processed_dir
                else:
                    target_dir = os.path.join(processed_dir, rel_path)
                
                os.makedirs(target_dir, exist_ok=True)
                
                file_srt_to_txt(file_path, target_dir, encoding)
                print(f"Fichier trouvé : {os.path.join(rel_path, file_name) if rel_path != '.' else file_name}")
                
    print(f"\nTerminé ! Fichiers enregistrés dans : {processed_dir}")

if __name__ == '__main__':
    main()