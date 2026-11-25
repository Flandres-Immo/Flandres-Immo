
import pandas as pd

def nettoyer_csv(chemin_fichier, chemin_sortie):

    # 1. Lire le fichier CSV
    df = pd.read_csv(chemin_fichier)

    # 2. Nettoyer les noms des colonnes
    df.columns = df.columns.str.strip()

    # 3. Supprimer les colonnes inutiles
    colonnes_a_supprimer = [
        "ancien_code_commune", "ancien_nom_commune","adresse_nom_voie","code_nature_culture","nature_culture",	
                     "code_nature_culture_speciale","nature_culture_speciale",
                     "adresse_suffixe", "lot5_numero",	"lot5_surface_carrez", "longitude",
                     "latitude","section_prefixe",
                     "lot3_numero","lot3_surface_carrez","lot4_numero","lot4_surface_carrez",
                     "ancien_id_parcelle","numero_volume", "lot1_surface_carrez", "lot2_numero", "lot1_numero","lot2_surface_carrez",
                     "adresse_numero","adresse_code_voie","numero_disposition" , "id_parcelle","nombre_lots", "code_type_local"
    ]

    df = df.drop(columns=colonnes_a_supprimer, errors="ignore")

    # 4. Supprimer les doublons
    df = df.drop_duplicates()

    # 5. Supprimer les lignes sans type_local
    df = df.dropna(subset=["type_local"])

    # 6. Convertir les colonnes numériques
    colonnes_numeriques = [
        "code_postal",
        "nombre_pieces_principales",
        "surface_reelle_bati",
        "surface_terrain",
        "code_commune",
        "code_departement"
    ]

    for colonne in colonnes_numeriques:
        if colonne in df.columns:
            df[colonne] = pd.to_numeric(
                df[colonne], errors="coerce"
            ).astype("Int64")

    if "date_mutation" in df.columns:
     df["date_mutation"] = pd.to_datetime(
        df["date_mutation"],
        errors="coerce",
        dayfirst=True
    )      

    # 7. Convertir la valeur foncière
    if "valeur_fonciere" in df.columns:
        df["valeur_fonciere"] = pd.to_numeric(
            df["valeur_fonciere"], errors="coerce"
        )
    df = df.drop_duplicates()    
    # 8. laise que appertement et maison 
    df = df[df["type_local"].isin(["Maison", "Appartement"])]

    # supprime les doublanat 
    df = df.drop_duplicates()
    # 9. Enregistrer le fichier nettoyé
    df.to_csv(chemin_sortie, index=False)

    print("Nombre de lignes :", len(df))

    return df

df_clean = nettoyer_csv(
    "./data/dvf Alpes Maritimes.csv",
    "./data_clean/dvf_alpes_maritimes_clean.csv"
)