"""
5_exporter_powerbi.py — Exporte l'entrepot en CSV prets a etre importes dans Power BI.

Power BI Desktop n'a pas de connecteur natif pour SQLite (il faudrait installer un
pilote ODBC tiers). L'export CSV est donc le chemin le plus court et le plus fiable
vers le rapport, et il reste lisible directement sur GitHub.

Trois precautions, chacune corrigeant un probleme reel d'import :

  1. UTF-8 AVEC BOM. Sans le BOM, Power BI applique l'encodage systeme (1252 sur
     une machine francophone) et 'Vêtements techniques' arrive en 'VÃªtements'.
  2. Separateur decimal POINT, sans separateur de milliers. Power BI interprete les
     nombres selon les paramètres regionaux du fichier ; un '1 234,56' exporte tel
     quel devient du texte, et toute mesure construite dessus renvoie une erreur.
  3. Dates au format ISO AAAA-MM-JJ, jamais JJ/MM/AAAA. Sur une machine configuree
     en anglais, '03/05/2025' serait lu comme le 5 mars au lieu du 3 mai — l'erreur
     est silencieuse et ne se voit qu'au moment ou la saisonnalite parait absurde.

Sortie : data/powerbi/*.csv (une table = un fichier)
"""

from __future__ import annotations

import csv
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "data", "entrepot", "boreal.db")
SORTIE = os.path.join(BASE, "data", "powerbi")
os.makedirs(SORTIE, exist_ok=True)

TABLES = [
    "dim_date", "dim_client", "dim_produit", "dim_fournisseur", "dim_employe",
    "dim_entrepot", "dim_canal_marketing",
    "fait_ventes", "fait_achats", "fait_stock", "fait_paie", "fait_marketing",
    "fait_charges", "qualite_rejets",
]

cx = sqlite3.connect(DB)
cx.row_factory = sqlite3.Row

total_lignes = 0
resume = []
for table in TABLES:
    lignes = cx.execute(f"SELECT * FROM {table}").fetchall()
    colonnes = [d[0] for d in cx.execute(f"SELECT * FROM {table} LIMIT 0").description]
    chemin = os.path.join(SORTIE, f"{table}.csv")

    # newline='' : impose des fins de ligne CRLF coherentes, quel que soit l'OS.
    # utf-8-sig : ecrit le BOM que Power BI utilise pour detecter l'encodage.
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        w.writerow(colonnes)
        for lg in lignes:
            w.writerow(["" if v is None else v for v in lg])

    taille_ko = os.path.getsize(chemin) / 1024
    resume.append((table, len(lignes), len(colonnes), taille_ko))
    total_lignes += len(lignes)

# Fiche d'accompagnement : ce que contient chaque fichier et a quel grain.
GRAINS = {
    "dim_date": "1 ligne par jour (2024-01-01 au 2026-06-30)",
    "dim_client": "1 ligne par client, apres fusion des fiches en double",
    "dim_produit": "1 ligne par article du catalogue",
    "dim_fournisseur": "1 ligne par fournisseur",
    "dim_employe": "1 ligne par employe",
    "dim_entrepot": "1 ligne par entrepot",
    "dim_canal_marketing": "1 ligne par canal",
    "fait_ventes": "1 ligne par article dans une commande client",
    "fait_achats": "1 ligne par article dans une commande fournisseur",
    "fait_stock": "1 photo mensuelle par article et par entrepot (NE PAS SOMMER dans le temps)",
    "fait_paie": "1 ligne par employe et par mois",
    "fait_marketing": "1 ligne par canal et par mois",
    "fait_charges": "1 ligne par categorie de charge, entrepot et mois",
    "qualite_rejets": "1 ligne par anomalie rencontree par l'ETL",
}

with open(os.path.join(SORTIE, "_CONTENU.md"), "w", encoding="utf-8") as f:
    f.write("# Contenu de l'export Power BI\n\n")
    f.write("_Genere par `Python/5_exporter_powerbi.py`. "
            "Encodage UTF-8 avec BOM, separateur `,`, decimale `.`, dates ISO._\n\n")
    f.write("| Fichier | Lignes | Colonnes | Taille | Grain |\n|---|---:|---:|---:|---|\n")
    for table, n, c, ko in resume:
        f.write(f"| `{table}.csv` | {n:,} | {c} | {ko:,.0f} Ko | {GRAINS[table]} |\n"
                .replace(",", " "))

print(f"Export Power BI ecrit dans {os.path.relpath(SORTIE, BASE)}/")
for table, n, c, ko in resume:
    print(f"  {table:<22} {n:>7,} lignes  {c:>2} colonnes  {ko:>7,.0f} Ko".replace(",", " "))
print(f"  {'TOTAL':<22} {total_lignes:>7,} lignes".replace(",", " "))
cx.close()
