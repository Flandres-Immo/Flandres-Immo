# Flandres-Immo
Projet Immobilier Hauts-de-France - Dashboard des ventes de maisons et appartements

## Introduction

Ce projet a pour objectif ...

## Architecture du projet

```
Flandres-Immo/
│
├── Data/
│   ├── Bronze/
│   │   ├── dvf Alpes Maritimes.csv 
│   │   ⋮
│   │ 
│   ├── Silver/
│   │   ├── dvf Alpes Maritimes.csv 
│   │   ⋮
│
├── Database/
│   ├── scriptCreationDB.py
|   └── dashboard.duckdb
|
├── Docs/
│   ├── guide-dutilisation-des-donnees.pdf
│   └── note-methodologique.pdf
│
├── Nettoyage/
│   ├── script.py
│   └── agregation.py
│
├── Analyse/
│   ├── volumetrie.py
│   └── statistiques.py
│
├── Images/
│   └── Dashboard.png
│
├── Pages/
│   ├── 1_page.py
│   ├── 2_page.py
│   │   ⋮
│
├── streamlitApp.py
├── requirements.txt
└── README.md
```

## Sources des données

[Data Gouv loyers-prix-et-rendement-locatif-brut-par-commune-millesime-2026](https://www.data.gouv.fr/datasets/loyers-prix-et-rendement-locatif-brut-par-commune-millesime-2026?utm_source=chatgpt.com&resource_id=776bd0d6-23b0-4e93-a7af-02677374e713)

[Statistiques DVF](https://www.data.gouv.fr/datasets/statistiques-dvf)

[Explore Data Gouv](https://explore.data.gouv.fr/fr/immobilier?onglet=carte&filtre=tous)

[Taux crédits](https://www.magnolia.fr/pret-immobilier/taux/historique)

[Revenus communes](https://www.data.gouv.fr/datasets/revenus-a-la-commune-en-france?utm_source=chatgpt.com&resource_id=d4d11259-964b-4c39-b81a-73bb735582e6)

[Loyers communes](https://www.data.gouv.fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2025?utm_source=chatgpt.com)

Toutes les données sont ici :
[Google Drive](https://drive.google.com/drive/folders/1v3lk3WeW6DYH5Ws5RH9IZJtzijcrBrjb?usp=drive_link)

## Etapes à suivre

- Faire un "git clone" du repository
- Mettre les fichiers brutes CSV dans le dossier Data/Bronze
- lancer le script : Nettoyage/scriptNettoyage.py
  (cela va remplir le dossier Data/silver avec les données  nettoyées)
- lancer le script : Database/scriptCreationDB.py
  (cela va créer la base de donnée et le fichier dashboard.duckdb)
- ...
