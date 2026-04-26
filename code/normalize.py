import os
import re
import pandas as pd

def nettoyer_texte_sous_titres(texte):
    """
    Fonction pour nettoyer le texte des sous-titres :
    Supprime les timecodes, les balises HTML, les noms des personnages et les bruitages.
    """
    # 1. Supprimer les timecodes (ex: 00:01:23,456 --> 00:01:25,678)
    texte = re.sub(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', '', texte)
    
    # 2. Supprimer les numéros de séquence
    texte = re.sub(r'^\d+$', '', texte, flags=re.MULTILINE)
    
    # 3. Supprimer les balises HTML (ex: <i>, </i>)
    texte = re.sub(r'<[^>]+>', '', texte)
    
    # 4. Supprimer les noms des locuteurs (limité à 50 caractères pour éviter les bugs)
    texte = re.sub(r'^[A-Z\s]{1,50}:', '', texte, flags=re.MULTILINE)
    
    # 5. Supprimer les effets sonores entre crochets ou parenthèses
    texte = re.sub(r'\[.*?\]|\(.*?\)', '', texte)
    
    # 6. Remplacer les sauts de ligne par des espaces
    texte = texte.replace('\n', ' ')
    texte = re.sub(r'\s+', ' ', texte).strip()
    
    # 7. Convertir en minuscules
    return texte.lower()

def obtenir_decennie(annee):
    """
    Calcule la décennie mathématiquement (ex: 1954 -> 1950s).
    """
    decennie = (annee // 10) * 10
    return f"{decennie}s"

# --- LOGIQUE PRINCIPALE ---

# Remplacez par le chemin absolu si le script ne trouve pas le dossier
dossier_principal = "/Users/serafimaklimova/PluriTAL/Traitement statistique des données/projet/TSD_projet_M1/data/raw"
jeu_de_donnees = []
compteur = 0 

print("Début du script de création du corpus...")

if not os.path.exists(dossier_principal):
    print(f"\n[ERREUR] Le dossier '{dossier_principal}' est introuvable !")
    exit()

print("Dossier trouvé ! Extraction en cours...\n")

for sous_dossier, dossiers, fichiers in os.walk(dossier_principal):
    for fichier in fichiers:
        if fichier.endswith('.srt'):
            chemin_fichier = os.path.join(sous_dossier, fichier)
            
            compteur += 1
            print(f"[{compteur}] Traitement : {fichier} ...", end=" ")
            
            # Extraction de la décennie depuis le nom du dossier (ex: 1950s, 1960s)
            nom_sous_dossier = os.path.basename(sous_dossier)
            correspondance_decennie = re.search(r'(19\d{2}s|20\d{2}s)', nom_sous_dossier)
            if not correspondance_decennie:
                print("IGNORÉ (Décennie introuvable dans le dossier)")
                continue 
                
            decennie = correspondance_decennie.group(1)
            # Extraire l'année à partir de la décennie (ex: 1950s -> 1955)
            annee_decennie = int(decennie[:4])
            annee = annee_decennie + 5  # Utiliser le milieu de la décennie
            
            # Extraction de la catégorie directement depuis le nom du fichier
            nom_fichier_minuscule = fichier.lower()
            if "oscar" in nom_fichier_minuscule:
                categorie = "Oscar"
            elif "blockbuster" in nom_fichier_minuscule:
                categorie = "Blockbuster"
            else:
                categorie = "Inconnu"
                
            # Lecture du fichier avec gestion d'encodage
            try:
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    texte_brut = f.read()
            except UnicodeDecodeError:
                with open(chemin_fichier, 'r', encoding='latin-1') as f:
                    texte_brut = f.read()
                    
            texte_propre = nettoyer_texte_sous_titres(texte_brut)
            
            # Vérification de la longueur du texte (ignorer les fichiers vides ou corrompus)
            if len(texte_propre) > 100:
                jeu_de_donnees.append({
                    "film": fichier.replace('.srt', ''), # On enlève l'extension .srt pour faire plus propre
                    "annee": annee,
                    "decennie": decennie,
                    "categorie": categorie,
                    "texte": texte_propre
                })
                print("OK")
            else:
                print("IGNORÉ (Texte trop court)")

# Création du DataFrame
df = pd.DataFrame(jeu_de_donnees)
nom_fichier_sortie = "subtitles_dataset.csv"

if not df.empty:
    df.to_csv(nom_fichier_sortie, index=False, encoding='utf-8')
    print("\n" + "="*40)
    print("--- EXTRACTION TERMINÉE AVEC SUCCÈS ---")
    print("="*40)
    print(f"Nombre total de films traités : {len(df)}")
    print(f"Fichier sauvegardé sous : {nom_fichier_sortie}\n")
    
    print("Répartition par décennies :")
    print(df['decennie'].value_counts().sort_index())
    
    print("\nRépartition par catégories :")
    print(df['categorie'].value_counts())
else:
    print("\n[ERREUR] Aucun fichier valide n'a été trouvé.")