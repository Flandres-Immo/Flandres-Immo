# Flandres-Immo
Projet Immobilier Hauts-de-France - Dashboard des ventes de maisons et appartements

## Cleaning DVF CSV files

Run the reusable cleaning workflow with an explicit input and output path:

```powershell
python clean_dvf.py "raw_data/dvf Bouche du Rhone.csv" "bouched_rohne/bdr_clean_script.csv"
```

The script removes exact duplicates from the full source rows before dropping
columns, then removes duplicate rows in the projected output as requested. It
reports both counts, filters the configured property types, validates the
Maison/Appartement type codes, preserves postal codes as text, and leaves
numeric missing values unchanged. It will not overwrite an existing output
unless `--overwrite` is supplied.
