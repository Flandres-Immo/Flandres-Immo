import os
import sys
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 20)

# Folders with data
PATH_FOLDER_SOURCE = "../Data perso/DATA BRONZE/"
PATH_FOLDER_TARGET = "../Data perso/DATA SILVER/"

# Filenames

# File Ille et Vilaine
name_iev = "Ille et Vilaine"
filename_iev = "dvf Ille et Vilaine.csv"
# File Loire Atlantique
name_la = "Loire Atlantique"
filename_la  = "dvf Loire Atlantique.csv"
# File Rhone
name_r = "Rhone"
filename_r  = "dvf Rhone.csv"
# Indicateurs loyers maison.csv
name_lm = "Indicateurs loyers maison"
filename_lm = "Indicateurs loyers maison.csv"

lst_names = [name_iev, name_la, name_r]
lst_filenames = [filename_iev, filename_la, filename_r]

ENCODING_UTF8 = 'utf-8'

COLUMNS_TO_KEEP = [
    'id_mutation', 
    'date_mutation', 
    'nature_mutation', 
    'valeur_fonciere', 
    'code_postal', 
    'code_commune', 
    'nom_commune', 
    'code_departement', 
    'code_type_local', 
    'type_local', 
    'surface_reelle_bati', 
    'nombre_pieces_principales', 
    'surface_terrain'
]


def nettoyage(file_source:str, file_target:str) -> None:
    '''
        Nettoyage du fichier file_source

        Args:

        Return:

    '''
    print(f'=== CLEANING FILE : {file_source} ===')

    df = pd.read_csv(file_source, encoding=ENCODING_UTF8, sep=',')
    print(f'Initial shape : {df.shape}')

    # On conserve certaines colonnes :
    df = df[COLUMNS_TO_KEEP]

    # On conserve uniquement les maisons et appartements
    df = df[df['type_local'].isin(['Maison', 'Appartement'])]
    print(f'Shape Après conservation des maisons et appartements : {df.shape}')

    # Suppression des lignes ayant un 'code_type_local' vide
    df = df.dropna(subset=['code_type_local'])
    print(f"Shape Après suppression des 'code_type_local' vides : {df.shape}")

    # ----------------------------
    # Conversion des types
    # ----------------------------

    # Conversion en Pandas datetime et errors='coerce' remplace les erreurs par NaN
    df["date_mutation"] = pd.to_datetime(df["date_mutation"], format="%Y-%m-%d", errors="coerce")

    df['valeur_fonciere'] = df['valeur_fonciere'].fillna(0)
    # Conversion en numérique et errors='coerce' remplace les erreurs par NaN
    df['valeur_fonciere'] = (pd.to_numeric(df['valeur_fonciere'], errors='coerce').round().astype('Int64'))

    df['code_postal'] = df['code_postal'].fillna(0)
    df['code_postal'] = pd.to_numeric(df['code_postal'], errors='coerce').astype('Int64')

    df['code_commune'] = df['code_commune'].fillna(0)
    df['code_commune'] = pd.to_numeric(df['code_commune'], errors='coerce').astype('Int64')

    df['code_departement'] = df['code_departement'].fillna(0)
    df['code_departement'] = pd.to_numeric(df['code_departement'], errors='coerce').astype('Int64')

    df['code_type_local'] = pd.to_numeric(df['code_type_local'], errors='coerce').astype('Int64')
    # Suppression des NaN
    df = df.dropna(subset=['code_type_local'])

    df['surface_reelle_bati'] = df['surface_reelle_bati'].fillna(0)
    df['surface_reelle_bati'] = (pd.to_numeric(df['surface_reelle_bati'], errors='coerce').round().astype('Int64'))

    df['nombre_pieces_principales'] = df['nombre_pieces_principales'].fillna(0)
    df['nombre_pieces_principales'] = (pd.to_numeric(df['nombre_pieces_principales'], errors='coerce').round().astype('Int64'))

    df['surface_terrain'] = df['surface_terrain'].fillna(0)
    df['surface_terrain'] = (pd.to_numeric(df['surface_terrain'], errors='coerce').round().astype('Int64'))

    df[['type_local', 'code_type_local']].value_counts()

    # Write file in target folder
    print(f'Ecriture du fichier {file_target}')
    df.to_csv(file_target)


if __name__ == '__main__':

    print("------------------")
    for filename in lst_filenames:
        print(filename)
        nettoyage(PATH_FOLDER_SOURCE + filename,
                       PATH_FOLDER_TARGET + filename)

