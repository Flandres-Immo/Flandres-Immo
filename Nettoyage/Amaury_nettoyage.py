"""Nettoie les données DVF pour l'étude des maisons et des appartements."""

from pathlib import Path

import pandas as pd

# Ouvrir et lire le fichier CSV DVF à partir de son chemin.
dossier_projet = Path(__file__).resolve().parent.parent
chemin_csv = dossier_projet / "drive-download-20261124T124355Z-1-001" / "dvf Paris.csv"

df = pd.read_csv(chemin_csv, dtype=str, keep_default_na=False)

# Garder uniquement les 12 colonnes utiles à l'étude, sans code_type_local.
# - id_mutation
# - date_mutation
# - nature_mutation
# - valeur_fonciere
# - code_postal
# - code_commune
# - nom_commune
# - code_departement
# - type_local
# - surface_reelle_bati
# - nombre_pieces_principales
# - surface_terrain
colonnes_a_garder = [
    "id_mutation",
    "date_mutation",
    "nature_mutation",
    "valeur_fonciere",
    "code_postal", --
    "code_commune",
    "nom_commune",
    "code_departement",
    "type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
]

df = df[colonnes_a_garder]

# Supprimer les lignes identiques sur les 12 colonnes et garder la première occurrence.
df = df.drop_duplicates()

# Retirer les espaces autour des valeurs.
df_nettoye = df.copy()

for colonne in df_nettoye.columns:
    df_nettoye[colonne] = df_nettoye[colonne].str.strip()

# Supprimer les en-têtes répétés.
entetes_repetes = df_nettoye.eq(df_nettoye.columns).all(axis=1)

print("En-têtes répétés supprimés :", entetes_repetes.sum())
df_nettoye = df_nettoye[~entetes_repetes]

# Contrôler les identifiants.
identifiants = df_nettoye["id_mutation"]

# Repérer les identifiants manquants ou vides
manquants = identifiants.isna() | identifiants.fillna("").eq("")

# Vérifier le format observé, par exemple 2026-607132
format_observe = identifiants.str.fullmatch(r"[0-9]{4}-[0-9]+", na=False)
formats_inhabituels = ~manquants & ~format_observe

print("Lignes sans identifiant :", manquants.sum())
print("Lignes avec un format inhabituel :", formats_inhabituels.sum())

# Afficher jusqu'à 10 exemples différents à examiner
print(identifiants[formats_inhabituels].drop_duplicates().head(10).tolist())

# Vérifier les dates et les convertir sans heure.
dates = df_nettoye["date_mutation"]

# Repérer les dates déjà vides
dates_vides = dates.isna() | dates.eq("")

# Convertir les dates. Les valeurs illisibles deviennent NaT
dates_converties = pd.to_datetime(dates, format="%Y-%m-%d", errors="coerce")
dates_invalides = ~dates_vides & dates_converties.isna()

print("Dates vides :", dates_vides.sum())
print("Dates invalides :", dates_invalides.sum())
df_nettoye["date_mutation"] = dates_converties.dt.date

# Contrôler les natures de mutation.
print(df_nettoye["nature_mutation"].value_counts())

# Écarter les lignes sans identifiant pour ce contrôle
avec_id = df_nettoye[df_nettoye["id_mutation"].fillna("") != ""]

nombre_de_libelles = avec_id.groupby("id_mutation")["nature_mutation"].nunique()
ids_a_verifier = nombre_de_libelles[nombre_de_libelles > 1]

print("Identifiants avec plusieurs libellés :", len(ids_a_verifier))
print(ids_a_verifier.head(10))

# Convertir les prix en euros entiers.
montants = df_nettoye["valeur_fonciere"]
montants_vides = montants.fillna("") == ""

montants_numeriques = pd.to_numeric(montants, errors="coerce")
montants_invalides = ~montants_vides & montants_numeriques.isna()

print("Montants vides :", montants_vides.sum())
print("Montants illisibles :", montants_invalides.sum())
print("Montants à zéro :", (montants_numeriques == 0).sum())
print("Montants négatifs :", (montants_numeriques < 0).sum())

df_nettoye["valeur_fonciere"] = montants_numeriques.round().astype("Int64")

# Contrôler les codes postaux.
codes = df_nettoye["code_postal"].fillna("")

codes_vides = codes == ""
format_correct = codes.str.fullmatch(r"[0-9]{5}")
codes_a_verifier = ~codes_vides & ~format_correct

print("Codes postaux vides :", codes_vides.sum())
print("Codes postaux au format inhabituel :", codes_a_verifier.sum())

# Contrôler les codes commune et les noms associés.
print("Codes commune vides :", (df_nettoye["code_commune"].fillna("") == "").sum())
noms_par_code = df_nettoye.groupby("code_commune")["nom_commune"].nunique()
codes_a_verifier = noms_par_code[noms_par_code != 1]

print("Codes commune à vérifier :", len(codes_a_verifier))

# Contrôler les codes département.
departements = df_nettoye["code_departement"].fillna("")

print("Codes département vides :", (departements == "").sum())
print(departements.value_counts())

# Convertir les surfaces bâties en entiers.
surfaces = pd.to_numeric(df_nettoye["surface_reelle_bati"], errors="coerce")
df_nettoye["surface_reelle_bati"] = surfaces.astype("Int64")

surfaces = df_nettoye["surface_reelle_bati"]

manquantes = surfaces.isna()
zeros = surfaces == 0
negatives = surfaces < 0

print("Surfaces manquantes :", manquantes.sum())
print("Surfaces à zéro :", zeros.sum())
print("Surfaces négatives :", negatives.sum())

# Garder les maisons et les appartements.
types_a_garder = ["Maison", "Appartement"]

df_nettoye = df_nettoye[df_nettoye["type_local"].isin(types_a_garder)].copy()

print(df_nettoye["type_local"].value_counts())

# Convertir le nombre de pièces en entiers.
pieces = df_nettoye["nombre_pieces_principales"]
pieces_vides = pieces.fillna("") == ""

pieces_numeriques = pd.to_numeric(pieces, errors="coerce")
pieces_illisibles = ~pieces_vides & pieces_numeriques.isna()
pieces_fractionnaires = pieces_numeriques.dropna() % 1 != 0

print("Champs vides :", pieces_vides.sum())
print("Valeurs illisibles :", pieces_illisibles.sum())
print("Valeurs à zéro :", (pieces_numeriques == 0).sum())
print("Valeurs négatives :", (pieces_numeriques < 0).sum())
print("Valeurs non entières :", pieces_fractionnaires.sum())

df_nettoye["nombre_pieces_principales"] = pieces_numeriques.astype("Int64")

# Convertir les surfaces de terrain.
terrains = df_nettoye["surface_terrain"]
terrains_vides = terrains.fillna("") == ""

terrains_numeriques = pd.to_numeric(terrains, errors="coerce")
terrains_illisibles = ~terrains_vides & terrains_numeriques.isna()

print("Surfaces vides :", terrains_vides.sum())
print("Surfaces illisibles :", terrains_illisibles.sum())
print("Surfaces à zéro :", (terrains_numeriques == 0).sum())
print("Surfaces négatives :", (terrains_numeriques < 0).sum())

df_nettoye["surface_terrain"] = terrains_numeriques

# Supprimer les doublons après les conversions.
avant = len(df_nettoye)
df_nettoye = df_nettoye.drop_duplicates()

print("Doublons supprimés :", avant - len(df_nettoye))
print("Lignes restantes :", len(df_nettoye))
print("Doublons restants :", df_nettoye.duplicated().sum())
print("Colonnes restantes :", len(df_nettoye.columns))

df = df_nettoye
