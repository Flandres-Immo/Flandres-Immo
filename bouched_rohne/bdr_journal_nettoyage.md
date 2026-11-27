# Journal de Suivi — Nettoyage des Données DVF (Bouches-du-Rhône)

**Fichier source :** `dvf Bouche du Rhone.csv`  
**Fichier nettoyé :** `bdr_clean.csv`  
**Script de référence :** `nettoyage_dvf.py`  
**Date du rapport :** 26 novembre 2026  

---

## 1. Vue d'ensemble des résultats

Le pipeline de nettoyage a permis de transformer les données brutes des Demandes de Valeurs Foncières (DVF) en un jeu de données structuré, dédoublonné et typé, prêt pour l'analyse immobilière.

| Indicateur | Jeu de données brut | Jeu de données nettoyé | Évolution |
| :--- | :---: | :---: | :---: |
| **Nombre de lignes** | 1 399 755 | 242 426 | -1 157 329 (-82,68 %) |
| **Nombre de colonnes** | 41 | 12 | -29 (-70,73 %) |
| **Valeurs manquantes (`NaN`)** | Présentes sur 33 colonnes | 0 | 100 % traitées |
| **Doublons exacts** | 1 032 285 (après réduction de colonnes) | 0 | 100 % supprimés |

---

## 2. Détail chronologique des étapes de nettoyage

### Étape 1 : Chargement et inspection initiale
* **Action :** Importation de `dvf Bouche du Rhone.csv` via `pandas` en forçant le typage de `code_postal` en `string` pour préserver les zéros initiaux.
* **Volume initial :** 1 399 755 lignes × 41 colonnes.

### Étape 2 : Sélection des variables et réduction de granularité
* **Suppression de colonnes (28 colonnes retirées) :** Élimination des informations d'adresse fine (`adresse_numero`, `adresse_nom_voie`, etc.), des identifiants cadastraux (`id_parcelle`, `ancien_id_parcelle`, `section_prefixe`), du détail des lots (`lot1_numero` à `lot5_surface_carrez`, `nombre_lots`), des natures de culture et des coordonnées GPS (`longitude`, `latitude`).
* **Contrôle de redondance et suppression :** Vérification de la correspondance exacte (0 incohérence) entre `type_local` et `code_type_local`, suivie de la suppression de `code_type_local`.
* **Résultat :** Conservation des **12 colonnes essentielles** à l'analyse des transactions.

### Étape 3 : Normalisation des chaînes de caractères et des en-têtes
* **Nettoyage des espaces :** Suppression des espaces superflus en début et fin de chaîne (`.strip()`) et remplacement des caractères invisibles (`\t`, `\r`, `\n`, espaces insécables) sur toutes les colonnes textuelles.
* **Correction des codes postaux :** Suppression du suffixe décimal `.0` (ex. `13008.0` → `13008`).
* **Suppression d'en-têtes parasites :** Élimination d'éventuelles lignes d'en-tête répétées (`id_mutation == "id_mutation"`).
* *Note technique : Cette étape est exécutée **avant** le dédoublonnage afin d'éviter que des différences invisibles de formatage ne masquent des lignes identiques.*

### Étape 4 : Dédoublonnage et filtrage métier
* **Suppression des doublons :** Élimination de **1 032 285 lignes en double** générées par l'agrégation au niveau transaction/bâtiment (après retrait des colonnes de parcelles et de lots).
* **Filtrage des types de biens :**
  * Suppression de **107 753 lignes** correspondant à `Dépendance`.
  * Suppression de **17 291 lignes** correspondant à `Local industriel. commercial ou assimilé`.
* **Volume restant :** **242 426 lignes** exploitables.

### Étape 5 : Imputation des valeurs manquantes
* **Variables catégorielles (`7 colonnes`) :** Remplacement des valeurs manquantes dans `id_mutation`, `nature_mutation`, `code_postal`, `code_commune`, `nom_commune`, `code_departement` et `type_local` par la mention **`"Non renseigné"`** (ex. : 75 816 valeurs imputées dans `type_local` et 2 071 dans `code_postal`).
* **Variables numériques (`4 colonnes`) :** Remplacement des valeurs manquantes dans `valeur_fonciere`, `surface_reelle_bati`, `nombre_pieces_principales` et `surface_terrain` par **`0`**.
* **Vérification :** `0` valeur manquante résiduelle sur l'ensemble de la table.

### Étape 6 : Typage final des données
* **Dates :** Conversion de `date_mutation` au format standard `datetime64` (0 erreur de conversion).
* **Nombres :** Conversion stricte de `valeur_fonciere`, `surface_reelle_bati`, `nombre_pieces_principales` et `surface_terrain` en format numérique (`float64`).

### Étape 7 : Exportation
* **Sauvegarde :** Exportation du jeu de données nettoyé vers **`bdr_clean.csv`** sans index de ligne.

---

## 3. Structure finale du jeu de données (`bdr_clean.csv`)

| Colonne | Type final | Description / Rôle |
| :--- | :--- | :--- |
| `id_mutation` | `string` | Identifiant unique de la transaction immobilière |
| `date_mutation` | `datetime64` | Date de signature de l'acte |
| `nature_mutation` | `string` | Nature de la mutation (ex. *Vente*, *VEFA*) |
| `valeur_fonciere` | `float64` | Montant global de la transaction en euros |
| `code_postal` | `string` | Code postal à 5 chiffres (ou `"Non renseigné"`) |
| `code_commune` | `string` | Code INSEE de la commune |
| `nom_commune` | `string` | Libellé de la commune (ex. *Marseille 8Eme*, *Aubagne*) |
| `code_departement` | `string` | Code du département (`13`) |
| `type_local` | `string` | Catégorie du bien (*Appartement*, *Maison*, *Non renseigné*) |
| `surface_reelle_bati` | `float64` | Surface bâtie mesurée en m² |
| `nombre_pieces_principales` | `float64` | Nombre de pièces principales |
| `surface_terrain` | `float64` | Surface du terrain associée en m² |

---

## 4. Points de vigilance pour l'analyse
1. **Imputation à `0` :** Les transactions sans `valeur_fonciere` (1 292 lignes) ou sans `surface_reelle_bati` (75 830 lignes) ayant été remplies par `0`, il conviendra de filtrer `valeur_fonciere > 0` et `surface_reelle_bati > 0` avant tout calcul de prix moyen au m².
2. **Mutations multi-biens :** Lorsqu'une même transaction (`id_mutation`) porte à la fois sur une maison et un appartement, la `valeur_fonciere` globale est répétée sur chaque ligne du bien ; éviter de sommer directement `valeur_fonciere` sans dédoublonner par `id_mutation`.
