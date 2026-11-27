import logging
from pathlib import Path
import pandas as pd

# Configuration du journal de suivi dans la console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


COLONNES_A_CONSERVER = [
    "id_mutation",
    "date_mutation",
    "nature_mutation",
    "valeur_fonciere",
    "code_postal",
    "code_commune",
    "nom_commune",
    "code_departement",
    "type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
]

TYPES_LOCAUX_CONSERVES = [
    "Maison",
    "Appartement",
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
    logger.info("1. Chargement du fichier : %s", chemin_fichier)
    df = pd.read_csv(
        chemin_fichier,
        dtype={"code_postal": "string"},
        low_memory=False,
    )
    logger.info(
        "   -> Données initiales : %s lignes | %d colonnes",
        f"{len(df):,}",
        df.shape[1],
    )
    return df


def selectionner_et_valider_colonnes(
    df: pd.DataFrame, colonnes_a_conserver: list[str]
) -> pd.DataFrame:
    """Vérifie la présence et la cohérence des colonnes requises, puis ne conserve que la liste blanche."""
    colonnes_manquantes = [c for c in colonnes_a_conserver if c not in df.columns]
    if colonnes_manquantes:
        raise ValueError(
            f"Colonnes obligatoires manquantes dans le fichier source : {colonnes_manquantes}"
        )

    # Validation de cohérence entre type_local et code_type_local si présent
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

    nb_cols_avant = len(df.columns)
    df = df[colonnes_a_conserver].copy()
    nb_cols_apres = len(df.columns)
    logger.info(
        "2. Sélection des colonnes : %d colonnes conservées (-%d colonnes écartées)",
        nb_cols_apres,
        nb_cols_avant - nb_cols_apres,
    )
    return df


def nettoyer_chaines_et_entetes(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les espaces superflus, les caractères invisibles, corrige les codes postaux et retire les en-têtes répétés."""
    df = df.copy()
    nb_lignes_avant = len(df)

    # Suppression des éventuelles lignes d'en-tête répétées dans le fichier
    entete_repetee = df["id_mutation"].astype("string").str.strip().eq("id_mutation")
    df = df.loc[~entete_repetee].copy()
    nb_entetes_supprimes = nb_lignes_avant - len(df)

    # Normalisation des espaces et conversion des chaînes vides en NA
    colonnes_texte = df.select_dtypes(include=["object", "string"]).columns
    for col in colonnes_texte:
        df[col] = (
            df[col]
            .astype("string")
            .str.replace(r"[\t\r\n\u00A0\u2007\u202F\u200B\uFEFF]+", " ", regex=True)
            .str.strip()
            .replace("", pd.NA)
        )

    # Nettoyage des suffixes '.0' sur les codes postaux
    if "code_postal" in df.columns:
        df["code_postal"] = df["code_postal"].str.replace(r"\.0$", "", regex=True)

    logger.info(
        "3. Normalisation du texte & en-têtes : -%s lignes d'en-tête répétées -> %s lignes restantes",
        f"{nb_entetes_supprimes:,}",
        f"{len(df):,}",
    )
    return df


def dedoublonner_et_filtrer(
    df: pd.DataFrame, types_conserves: list[str]
) -> pd.DataFrame:
    """Supprime les doublons exacts et ne conserve que les biens résidentiels (Maison, Appartement)."""
    nb_lignes_avant = len(df)
    df = df.drop_duplicates().copy()
    logger.info(
        "4a. Dédoublonnage : -%s doublons supprimés -> %s lignes restantes",
        f"{nb_lignes_avant - len(df):,}",
        f"{len(df):,}",
    )

    nb_avant_filtre = len(df)
    types_normalises = [t.strip().casefold() for t in types_conserves]
    masque_residentiel = (
        df["type_local"].astype("string").str.casefold().isin(types_normalises)
    )
    df = df.loc[masque_residentiel].copy()
    logger.info(
        "4b. Filtrage résidentiel %s : -%s lignes hors périmètre -> %s lignes restantes",
        types_conserves,
        f"{nb_avant_filtre - len(df):,}",
        f"{len(df):,}",
    )

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
    df[num_existantes] = df[num_existantes].apply(pd.to_numeric, errors="raise").fillna(0)


    logger.info(
        "5. Imputation des valeurs manquantes : %s cellules vides traitées (NA restants : %d)",
        f"{nb_na_avant:,}",
        int(df.isna().sum().sum()),
    )
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

    logger.info("6. Typage des données : dates et colonnes numériques converties avec succès")
    return df


def executer_pipeline_nettoyage(
    chemin_entree: str | Path, chemin_sortie: str | Path
) -> pd.DataFrame:
    """Exécute l'ensemble du pipeline de nettoyage DVF et exporte le résultat en CSV."""
    logger.info("=== DÉMARRAGE DU PIPELINE DE NETTOYAGE DVF ===")
    df_brut = charger_donnees(chemin_entree)
    nb_lignes_initial = len(df_brut)

    df_propre = (
        df_brut.pipe(
            selectionner_et_valider_colonnes,
            colonnes_a_conserver=COLONNES_A_CONSERVER,
        )
        .pipe(nettoyer_chaines_et_entetes)
        .pipe(dedoublonner_et_filtrer, types_conserves=TYPES_LOCAUX_CONSERVES)
        .pipe(
            imputer_valeurs_manquantes,
            colonnes_cat=COLONNES_CATEGORIELLES,
            colonnes_num=COLONNES_NUMERIQUES,
        )
        .pipe(convertir_types_donnees, colonnes_num=COLONNES_NUMERIQUES)
    )

    # Création automatique du dossier parent de sortie si nécessaire
    chemin_out = Path(chemin_sortie)
    chemin_out.parent.mkdir(parents=True, exist_ok=True)
    df_propre.to_csv(chemin_out, index=False)

    lignes_supprimees = nb_lignes_initial - len(df_propre)
    taux_reduction = (lignes_supprimees / nb_lignes_initial) * 100
    logger.info(
        "7. Export terminé : '%s' (%s lignes | %d colonnes)",
        chemin_out,
        f"{len(df_propre):,}",
        df_propre.shape[1],
    )
    logger.info(
        "=== BILAN : -%s lignes supprimées au total (-%.1f%%) ===",
        f"{lignes_supprimees:,}",
        taux_reduction,
    )
    return df_propre


def nettoyer_dossier_dvf(
    dossier_entree: str | Path, dossier_sortie: str | Path
) -> None:
    """Parcourt tous les fichiers CSV d'un dossier et exécute le pipeline de nettoyage sur chacun."""
    dossier_in = Path(dossier_entree)
    dossier_out = Path(dossier_sortie)
    dossier_out.mkdir(parents=True, exist_ok=True)

    fichiers_csv = sorted(dossier_in.glob("*.csv"))
    if not fichiers_csv:
        logger.warning("Aucun fichier CSV trouvé dans '%s'.", dossier_in)
        return

    logger.info("=== TRAITEMENT PAR LOT : %d fichier(s) détecté(s) ===", len(fichiers_csv))

    for idx, fichier in enumerate(fichiers_csv, start=1):
        nom_propre = fichier.stem.lower().replace(" ", "_") + "_clean.csv"
        chemin_sortie = dossier_out / nom_propre
        logger.info("\n--- [%d/%d] Traitement de '%s' ---", idx, len(fichiers_csv), fichier.name)

        try:
            executer_pipeline_nettoyage(fichier, chemin_sortie)
        except Exception as e:
            logger.error("Échec sur '%s' : %s", fichier.name, e)


if __name__ == "__main__":
    DOSSIER_ENTREE = Path("../raw_data")
    DOSSIER_SORTIE = Path("./clean_data")

    nettoyer_dossier_dvf(DOSSIER_ENTREE, DOSSIER_SORTIE)
