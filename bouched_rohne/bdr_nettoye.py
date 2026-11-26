from pathlib import Path
import pandas as pd


COLONNES_A_SUPPRIMER = [
    "adresse_numero",
    "adresse_suffixe",
    "adresse_nom_voie",
    "adresse_code_voie",
    "ancien_code_commune",
    "ancien_nom_commune",
    "id_parcelle",
    "ancien_id_parcelle",
    "numero_volume",
    "lot1_numero",
    "lot1_surface_carrez",
    "lot2_numero",
    "lot2_surface_carrez",
    "lot3_numero",
    "lot3_surface_carrez",
    "lot4_numero",
    "lot4_surface_carrez",
    "lot5_numero",
    "lot5_surface_carrez",
    "nombre_lots",
    "code_nature_culture",
    "nature_culture",
    "code_nature_culture_speciale",
    "nature_culture_speciale",
    "longitude",
    "latitude",
    "section_prefixe",
    "numero_disposition",
]

TYPES_LOCAUX_EXCLUS = [
    "Dépendance",
    "Local industriel. commercial ou assimilé",
]

COLONNES_CATEGORIELLES = [
    "id_mutation",
    "nature_mutation",
    "code_postal",
    "code_commune",
    "nom_commune",
    "code_departement",
    "type_local",
]

COLONNES_NUMERIQUES = [
    "valeur_fonciere",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
]


def charger_donnees(chemin_fichier: str | Path) -> pd.DataFrame:
    """Charge le fichier CSV brut DVF en conservant les codes postaux au format texte."""
    return pd.read_csv(
        chemin_fichier,
        dtype={"code_postal": "string"},
        low_memory=False,
    )


def selectionner_et_valider_colonnes(
    df: pd.DataFrame, colonnes_a_supprimer: list[str]
) -> pd.DataFrame:
    """Supprime les colonnes inutiles et retire code_type_local après vérification de cohérence."""
    df = df.drop(columns=colonnes_a_supprimer, errors="ignore").copy()

    if {"type_local", "code_type_local"}.issubset(df.columns):
        nom_type = df["type_local"].astype("string").str.strip().str.casefold()
        code = pd.to_numeric(df["code_type_local"], errors="coerce")
        incoherence = (nom_type.eq("maison") & code.ne(1.0)) | (
            nom_type.eq("appartement") & code.ne(2.0)
        )
        if incoherence.any():
            raise ValueError(
                f"{int(incoherence.sum())} incohérences détectées entre type_local et code_type_local."
            )
        df = df.drop(columns=["code_type_local"])

    return df


def nettoyer_chaines_et_entetes(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les espaces superflus, les caractères invisibles, corrige les codes postaux et retire les en-têtes répétés."""
    df = df.copy()

    # Suppression des éventuelles lignes d'en-tête répétées dans le fichier
    entete_repetee = df["id_mutation"].astype("string").str.strip().eq("id_mutation")
    df = df.loc[~entete_repetee].copy()

    # Suppression des espaces en début/fin et normalisation des caractères invisibles
    colonnes_texte = df.select_dtypes(include=["object", "string"]).columns
    for col in colonnes_texte:
        df[col] = (
            df[col]
            .astype("string")
            .str.replace(r"[\t\r\n\u00A0\u2007\u202F\u200B\uFEFF]+", " ", regex=True)
            .str.strip()
        )

    # Nettoyage des suffixes '.0' sur les codes postaux
    if "code_postal" in df.columns:
        df["code_postal"] = df["code_postal"].str.replace(r"\.0$", "", regex=True)

    return df


def dedoublonner_et_filtrer(
    df: pd.DataFrame, types_exclus: list[str]
) -> pd.DataFrame:
    """Supprime les doublons exacts (après nettoyage du texte) et exclut les types de biens non souhaités."""
    df = df.drop_duplicates().copy()

    for type_bien in types_exclus:
        masque = df["type_local"].str.contains(
            type_bien, case=False, na=False, regex=False
        )
        df = df.loc[~masque].copy()

    return df


def imputer_valeurs_manquantes(
    df: pd.DataFrame, colonnes_cat: list[str], colonnes_num: list[str]
) -> pd.DataFrame:
    """Remplace les valeurs manquantes textuelles par 'Non renseigné' et numériques par 0."""
    df = df.copy()
    nb_na_avant = int(df.isna().sum().sum())
    
    cat_existantes = [c for c in colonnes_cat if c in df.columns]
    df[cat_existantes] = df[cat_existantes].astype("string").fillna("Non renseigné")

    num_existantes = [c for c in colonnes_num if c in df.columns]
    df[num_existantes] = df[num_existantes].fillna(0)

    "5. Imputation des valeurs manquantes : %s cellules vides traitées (NA restants : %d)",
    f"{nb_na_avant:,}",
    int(df.isna().sum().sum()),

    return df


def convertir_types_donnees(df: pd.DataFrame, colonnes_num: list[str]) -> pd.DataFrame:
    """Convertit date_mutation en datetime64 et les colonnes numériques en float64."""
    df = df.copy()

    if "date_mutation" in df.columns:
        dates_origine = df["date_mutation"]
        dates_converties = pd.to_datetime(dates_origine, errors="coerce")
        invalides = dates_origine.notna() & dates_converties.isna()
        if invalides.any():
            raise ValueError(
                f"Échec de conversion pour {int(invalides.sum())} dates dans date_mutation."
            )
        df["date_mutation"] = dates_converties

    num_existantes = [c for c in colonnes_num if c in df.columns]
    df[num_existantes] = df[num_existantes].apply(pd.to_numeric, errors="raise")

    return df


def executer_pipeline_nettoyage(
    chemin_entree: str | Path, chemin_sortie: str | Path
) -> pd.DataFrame:
    """Exécute l'ensemble du pipeline de nettoyage DVF et exporte le résultat en CSV."""
    df = (
        charger_donnees(chemin_entree)
        .pipe(selectionner_et_valider_colonnes, colonnes_a_supprimer=COLONNES_A_SUPPRIMER)
        .pipe(nettoyer_chaines_et_entetes)
        .pipe(dedoublonner_et_filtrer, types_exclus=TYPES_LOCAUX_EXCLUS)
        .pipe(
            imputer_valeurs_manquantes,
            colonnes_cat=COLONNES_CATEGORIELLES,
            colonnes_num=COLONNES_NUMERIQUES,
        )
        .pipe(convertir_types_donnees, colonnes_num=COLONNES_NUMERIQUES)
    )

    df.to_csv(chemin_sortie, index=False)
    print(
        f"Nettoyage terminé. {len(df):,} lignes et {df.shape[1]} colonnes enregistrées dans {chemin_sortie}."
    )
    return df


if __name__ == "__main__":
    FICHIER_ENTREE = Path("./raw_data/dvf Bouche du Rhone.csv")
    FICHIER_SORTIE = Path("bdr_clean.csv")

    df_propre = executer_pipeline_nettoyage(FICHIER_ENTREE, FICHIER_SORTIE)
