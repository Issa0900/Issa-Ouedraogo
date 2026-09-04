"""
4_analyser.py — Execute les requetes de SQL/2_requetes_analyse.sql et publie les resultats.

Les chiffres cites dans le README proviennent tous de ce script : aucun n'est saisi
a la main. Relancer le pipeline regenere le rapport, et un chiffre du README qui ne
correspondrait plus se verrait immediatement.

Sortie : data/ANALYSE.md (tous les tableaux) + affichage console.
"""

from __future__ import annotations

import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "data", "entrepot", "boreal.db")
REQUETES = os.path.join(BASE, "SQL", "2_requetes_analyse.sql")
SORTIE = os.path.join(BASE, "data", "ANALYSE.md")

TITRES = {
    "resultat_par_annee": "Compte de resultat simplifie",
    "marge_par_famille": "Marge brute par famille de produits",
    "cout_achat_par_fournisseur": "Evolution du cout d'achat par fournisseur",
    "impact_chiffre_derive": "Manque a gagner 2025 a cout d'achat 2024",
    "concentration_clients": "Concentration du chiffre d'affaires (top 10 clients)",
    "rotation_stock": "Rotation des stocks par entrepot",
    "delai_paiement": "Delai moyen d'encaissement et encours client",
    "performance_marketing": "Performance des canaux marketing",
    "masse_salariale": "Masse salariale rapportee au chiffre d'affaires",
    "roulement_personnel": "Taux de roulement par departement",
    "ponctualite_fournisseurs": "Ponctualite de livraison des fournisseurs",
    "saisonnalite": "Saisonnalite mensuelle du chiffre d'affaires",
    "qualite_donnees": "Journal de nettoyage par nature de defaut",
}

# Mise en forme francophone : espace comme separateur de milliers, virgule decimale.
# Le suffixe d'unite est deduit du nom de la colonne, ce qui evite d'avoir a le
# repeter dans chaque requete SQL.
import re as _re

POURCENTAGE = _re.compile(r"_pct$|^taux_")
POINTS = _re.compile(r"_points$")
JOURS = _re.compile(r"_jours$|^jours_")
MONTANT_PRECIS = _re.compile(r"^cout_unitaire")
MONTANT = _re.compile(r"^ca(_|$)|^marge|^cout|^stock_moyen$|^masse|^charges$|"
                      r"^marketing$|^resultat|^encours|^depense|^panier|^manque|_moyenne$")


def _nb(valeur: float, decimales: int) -> str:
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


def decouper(sql: str) -> list[tuple[str, str]]:
    """Isole chaque requete a partir de son marqueur '-- @nom'."""
    blocs = []
    nom, courant = None, []
    for ligne in sql.splitlines():
        marque = _re.match(r"^--\s*@(\w+)\s*$", ligne)
        if marque:
            if nom:
                blocs.append((nom, "\n".join(courant)))
            nom, courant = marque.group(1), []
        elif nom is not None:
            courant.append(ligne)
    if nom:
        blocs.append((nom, "\n".join(courant)))
    return blocs


def formater(colonne: str, valeur) -> str:
    if valeur is None:
        return "—"
    if not isinstance(valeur, (int, float)) or isinstance(valeur, bool):
        return str(valeur)
    signe = "+" if ("variation" in colonne and valeur > 0) else ""
    if POINTS.search(colonne):
        return f"{signe}{_nb(valeur, 1)} pts"
    if POURCENTAGE.search(colonne):
        return f"{signe}{_nb(valeur, 1)} %"
    if JOURS.search(colonne):
        return f"{_nb(valeur, 1).removesuffix(',0')} j"
    if MONTANT_PRECIS.match(colonne):
        return _nb(valeur, 2) + " $"
    if MONTANT.match(colonne):
        return _nb(valeur, 0) + " $"
    if isinstance(valeur, float):
        return _nb(valeur, 2)
    return _nb(valeur, 0) if abs(valeur) >= 10000 else str(valeur)


cx = sqlite3.connect(DB)
cx.row_factory = sqlite3.Row
with open(REQUETES, encoding="utf-8") as f:
    blocs = decouper(f.read())

md = ["# Resultats d'analyse — Boreal Distribution\n",
      "_Genere automatiquement par `Python/4_analyser.py` a partir de "
      "`SQL/2_requetes_analyse.sql`. Ne pas editer a la main._\n"]

resultats = {}
for nom, requete in blocs:
    lignes = [dict(r) for r in cx.execute(requete)]
    resultats[nom] = lignes
    titre = TITRES.get(nom, nom)
    md.append(f"\n## {titre}\n")
    md.append(f"<sub>Requete `@{nom}` — `SQL/2_requetes_analyse.sql`</sub>\n")
    if not lignes:
        md.append("\n_Aucun resultat._\n")
        continue
    colonnes = list(lignes[0].keys())
    md.append("\n| " + " | ".join(c.replace("_", " ") for c in colonnes) + " |")
    md.append("|" + "---|" * len(colonnes))
    for lg in lignes:
        md.append("| " + " | ".join(formater(c, lg[c]) for c in colonnes) + " |")

    print(f"\n=== {titre} ===")
    largeurs = [max(len(c), max(len(formater(c, lg[c])) for lg in lignes)) for c in colonnes]
    print("  " + "  ".join(c.ljust(w) for c, w in zip(colonnes, largeurs)))
    for lg in lignes[:12]:
        print("  " + "  ".join(formater(c, lg[c]).ljust(w) for c, w in zip(colonnes, largeurs)))
    if len(lignes) > 12:
        print(f"  ... {len(lignes) - 12} lignes supplementaires")

with open(SORTIE, "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")
print(f"\nRapport ecrit : {os.path.relpath(SORTIE, BASE)} ({len(blocs)} analyses)")
cx.close()
