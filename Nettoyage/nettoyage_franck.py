
import os
import sys
import numpy as np
import pandas as pd

# Folders with data
PATH_FOLDER_SOURCE = "../Data/Bronze/"
PATH_FOLDER_TARGET = "../Data/Silver/"

# Encoding
ENCODING_UTF8   = 'utf-8'
ENCODING_CP1252 = 'cp1252'

COLUMNS_DVF_TO_KEEP = [
    'id_mutation', 
    'date_mutation', 
    'nature_mutation', 
    'valeur_fonciere', 
    'code_postal', 
    'code_commune', 
    'nom_commune', 
    'code_departement', 
    'type_local', 
    'surface_reelle_bati', 
    'nombre_pieces_principales', 
    'surface_terrain'
]

COLUMNS_INDICATEURS_TO_KEEP = [
    'id_zone',
	'INSEE_C',
   	'LIBGEO',
   	'EPCI',
	'DEP',
    'REG',
    'loypredm2',
    'lwr.IPm2',
    'upr.IPm2',
    'TYPPRED',
    'nbobs_com',
    'nbobs_mail',	
    'R2_adj',
]


def nettoyage_dvf(filename:str) -> None:
    '''
        Nettoyage du fichier 'DVF' : filename
        (Conservation des colonnes strictement utiles)
        Ecrit un fichier nettoyé dans le dossier PATH_FOLDER_TARGET

        Args: filename: fichier de données à nettoyer

        Return: None
    '''

    print('=' * 80)
    text = f'CLEANING FILE : {filename}'
    print(f'===== {text:^68} =====')
    print('=' * 80 + '\n')

    print(f'Lecture du fichier : {PATH_FOLDER_SOURCE + filename}')
    print(f'*** Taille  du fichier : {os.path.getsize(PATH_FOLDER_SOURCE + filename)}')
    df = pd.read_csv(PATH_FOLDER_SOURCE + filename, encoding=ENCODING_UTF8, sep=',')
    print(f'Initial shape : {df.shape}')

    # On conserve certaines colonnes :
    df = df[COLUMNS_DVF_TO_KEEP]

    # On conserve uniquement les maisons et appartements
    df = df[df['type_local'].isin(['Maison', 'Appartement'])]
    print(f'Shape Après conservation des maisons et appartements : {df.shape}')

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

    df['surface_reelle_bati'] = df['surface_reelle_bati'].fillna(0)
    df['surface_reelle_bati'] = (pd.to_numeric(df['surface_reelle_bati'], errors='coerce').round().astype('Int64'))

    df['nombre_pieces_principales'] = df['nombre_pieces_principales'].fillna(0)
    df['nombre_pieces_principales'] = (pd.to_numeric(df['nombre_pieces_principales'], errors='coerce').round().astype('Int64'))

    df['surface_terrain'] = df['surface_terrain'].fillna(0)
    df['surface_terrain'] = (pd.to_numeric(df['surface_terrain'], errors='coerce').round().astype('Int64'))

    # Suppression des doublons
    df = df.drop_duplicates()
    print(f"Shape Après suppression des doublons : {df.shape}")

    # Write file in target folder
    print(f'Ecriture du fichier {PATH_FOLDER_TARGET + filename}')
    df.to_csv(PATH_FOLDER_TARGET + filename, encoding=ENCODING_UTF8, sep=',')
    
    # On affiche la taille finale du fichier 
    print(f'*** Taille  du fichier final : {os.path.getsize(PATH_FOLDER_TARGET + filename)}\n')



def nettoyage_indicateurs(filename:str) -> None:
    '''
        Nettoyage du fichier "Indicateurs" : filename
        Ecrit un fichier nettoyé dans le dossier PATH_FOLDER_TARGET

        Args: filename: fichier de données à nettoyer

        Return: None
    '''
    print('=' * 80)
    text = f'CLEANING FILE : {filename}'
    print(f'===== {text:^68} =====')
    print('=' * 80 + '\n')

    print(f'Lecture du fichier : {PATH_FOLDER_SOURCE + filename}')
    print(f'*** Taille  du fichier : {os.path.getsize(PATH_FOLDER_SOURCE + filename)}')
    df = pd.read_csv(PATH_FOLDER_SOURCE + filename, encoding=ENCODING_CP1252, sep=';')
    print(f'Initial shape : {df.shape}')

    # On conserve certaines colonnes :
    df = df[COLUMNS_INDICATEURS_TO_KEEP]

    # Conversion de types en entier
    colonnes = ['id_zone', 'INSEE_C', 'EPCI', 'DEP', 'REG',	'nbobs_com', 'nbobs_mail']
    df[colonnes] = df[colonnes].apply(pd.to_numeric, errors='coerce').astype('Int64')

    # Conversion de types en décimal avec 2 chiffres après la virgule
    colonnes = ['loypredm2', 'lwr.IPm2', 'upr.IPm2', 'R2_adj']
    df[colonnes] = df[colonnes].apply(
        lambda x: pd.to_numeric(
            x.str.replace(',', '.', regex=False),
            errors='coerce'
        )
    ).round(2)

    df = df.drop_duplicates()
    print(f"Shape Après suppression des doublons : {df.shape}")

    # Write file in target folder
    print(f'Ecriture du fichier {PATH_FOLDER_TARGET + filename}')
    df.to_csv(PATH_FOLDER_TARGET + filename, encoding=ENCODING_CP1252, sep=',')

    # On affiche la taille finale du fichier 
    print(f'*** Taille  du fichier final : {os.path.getsize(PATH_FOLDER_TARGET + filename)}\n')




if __name__ == '__main__':

    # On parcourt tous les fichiers
    # Selon le nom du fichier on applique la fonction de nettoyage correspondante
    for filename in os.listdir(PATH_FOLDER_SOURCE):

        if filename[:3].lower() == 'dvf':
            nettoyage_dvf(filename)

        if filename[:11].lower() == 'indicateurs':
            nettoyage_indicateurs(filename)
