import pandas as pd


# Fonction qui traite le fichier des revenus
def revenu(nom_fichier):

    df = pd.read_excel(nom_fichier)
   
    # Garder les colonnes utiles
    df = df[[
        "Code géographique",
        "[DISP] Nbre de ménages fiscaux",
        "Nom géographique GMS",
        "[DISP] Nbre de personnes dans les ménages fiscaux",
        "[DISP] Médiane (€)"
    ]].copy()
   
    print("Après sélection des colonnes :", df.shape)

    # Supprimer les NaN
    df = df.dropna()
    print("Après suppression des NaN :", df.shape)

    # Convertir le code en Int
    df["Code géographique"] = pd.to_numeric(
        df["Code géographique"],
        errors="coerce"
    ).astype("Int64")

    print("Après conversion du code :", df.shape)

    # Renommer les colonnes
    df = df.rename(columns={
        "Code géographique": "Code INSEE",
        "[DISP] Nbre de ménages fiscaux": "Nb de ménages fiscaux",
        "Nom géographique GMS": "Nom Commune",
        "[DISP] Nbre de personnes dans les ménages fiscaux": "Nb de personnes dans les ménages",
        "[DISP] Médiane (€)": "Médiane (€)"
    })

    # Supprimer les doublons
    df = df.dropna()
    df = df.drop_duplicates()
    print("Après suppression des doublons :", df.shape)
    print(df.duplicated().sum())

    return df

# Fonction qui traite le fichier des indicateurs de loyers
def indicateur_loyer(nom_fichier):

    df = pd.read_csv(
        nom_fichier,
        encoding="cp1252",
        sep=";"
    )

    df["loypredm2"] = (
        df["loypredm2"]
        .str.replace(",", ".", regex=False)
        .astype(float)
        .round(2)
    )

    colonnes_float = [
        "lwr.IPm2",
        "upr.IPm2",
        "R2_adj"
    ]

    for colonne in colonnes_float:
        df[colonne] = (
            df[colonne]
            .str.replace(",", ".", regex=False)
            .astype(float)
            .round(2)
        )

    colonnes_int = [
        "id_zone",
        "INSEE_C",
        "EPCI",
        "DEP"
    ]

    for colonne in colonnes_int:
        df[colonne] = pd.to_numeric(
            df[colonne],
            errors="coerce"
        ).astype("Int64")

    df = df.drop_duplicates()

    return df


# Fonction qui traite le fichier DVF
def dvf(nom_fichier):

    df = pd.read_csv(
        nom_fichier,
        encoding="cp1252",
        sep=";"
    )

    # Mettre ici tes traitements DVF

    df = df.drop_duplicates()

    return df


# Fonction principale
def traiter_fichier(nom_fichier):

    nom = nom_fichier.lower()

    if "revenu" in nom:
        df = revenu(nom_fichier)

    elif "loyer" in nom or "loyers" in nom:
        df = indicateur_loyer(nom_fichier)

    elif "dvf" in nom or "immobilier" in nom:
        df = dvf(nom_fichier)

    else:
        print("Type de fichier non reconnu")
        return None

    print("Fichier traité :", nom_fichier)
    print("Dimensions :", df.shape)

    return df
df_revenu = traiter_fichier(
    "./data/revenus-en-france-geoptis.xlsx"
)
print(df_revenu.shape)
df_revenu.to_csv("./data_clean/revenus_nettoyes.csv", index=False, encoding="utf-8-sig")

#df_loyer = traiter_fichier(
 #   "./data/Indicateurs loyers appartement 1 ou 2 pieces.csv"
#)

#df_dvf = traiter_fichier(
  #  "./data/dvf.csv"
#)

