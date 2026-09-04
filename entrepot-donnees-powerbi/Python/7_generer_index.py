"""
7_generer_index.py — Produit index.md (page du site) a partir de README.md.

Le portfolio est un site Jekyll : chaque projet expose un README.md (vitrine GitHub)
et un index.md (page du site). Les garder synchronises a la main les fait diverger ;
ce script derive le second du premier.

Une seule transformation est necessaire. Jekyll ne publie pas les dossiers exclus
dans _config.yml (data/, Python/, SQL/, PowerBI/) : les liens relatifs vers ces
fichiers fonctionnent sur GitHub mais seraient morts sur le site. Ils sont donc
reecrits vers GitHub. Les images d'assets/, elles, sont bien publiees et restent
en relatif.
"""

from __future__ import annotations

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJET = os.path.basename(BASE)
DEPOT = "https://github.com/Issa0900/Issa-Ouedraogo/blob/main"

with open(os.path.join(BASE, "README.md"), encoding="utf-8") as f:
    contenu = f.read()

titre = re.search(r"^#\s+(.+)$", contenu, re.M).group(1)
titre_propre = re.sub(r"^[^\w]+", "", titre).strip()


def reecrire(m: re.Match) -> str:
    cible = m.group(1)
    if cible.startswith("./assets/"):
        return m.group(0)
    return f"]({DEPOT}/{PROJET}/{cible[2:]})"


corps = re.sub(r"\]\((\./[^)]+)\)", reecrire, contenu)

sortie = (f"---\nlayout: project\ntitle: {titre_propre}\n---\n\n"
          f"{corps}\n\n[← Retour au portfolio](../)\n")

with open(os.path.join(BASE, "index.md"), "w", encoding="utf-8") as f:
    f.write(sortie)

print(f"index.md genere ({len(sortie.splitlines())} lignes) — titre : {titre_propre}")
