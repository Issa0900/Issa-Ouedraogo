"""
Récupère, pour chacune des 17 régions administratives, le contenu HTML de sa fiche
"Coup d'œil sur les régions" (ISQ) embarqué dans le JSON __NEXT_DATA__ de la page. Ces
fiches contiennent, en texte, plusieurs éditions (2022 à 2024) d'indicateurs clés :
population, taux de croissance, revenu disponible par habitant, taux de chômage. C'est la
seule voie scriptable trouvée : les tableaux dynamiques de la BDSO (statistique.quebec.ca)
n'exposent pas de lien CSV ni d'API publique — voir data/SOURCES.md.

Écrit un fichier HTML brut par région dans data/raw_isq/, à parser ensuite avec
3_extraire_indicateurs_isq.py.
"""

import json
import re
import time
from pathlib import Path

import requests

REGIONS = [
    ("abitibi-temiscamingue-panorama", "Abitibi-Témiscamingue"),
    ("bas-saint-laurent-panorama", "Bas-Saint-Laurent"),
    ("capitale-nationale-panorama", "Capitale-Nationale"),
    ("centre-du-quebec-panorama", "Centre-du-Québec"),
    ("chaudiere-appalaches-panorama", "Chaudière-Appalaches"),
    ("cote-nord-panorama", "Côte-Nord"),
    ("estrie-panorama", "Estrie"),
    ("gaspesie-iles-de-la-madeleine-panorama", "Gaspésie–Îles-de-la-Madeleine"),
    ("lanaudiere-panorama", "Lanaudière"),
    ("laurentides-panorama", "Laurentides"),
    ("laval-panorama", "Laval"),
    ("mauricie-panorama", "Mauricie"),
    ("monteregie-panorama", "Montérégie"),
    ("montreal-panorama", "Montréal"),
    ("nord-du-quebec-panorama", "Nord-du-Québec"),
    ("outaouais-panorama", "Outaouais"),
    ("saguenay-lac-saint-jean-panorama", "Saguenay–Lac-Saint-Jean"),
]

OUT = Path(__file__).resolve().parent.parent / "data" / "raw_isq"
OUT.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

for slug, nom in REGIONS:
    url = f"https://statistique.quebec.ca/fr/produit/publication/{slug}"
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
        data = json.loads(m.group(1))
        html = data["props"]["pageProps"]["data"]["html"]
        (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"OK  {nom} ({len(html)} car.)")
    except Exception as e:
        print(f"ERR {nom}: {e}")
    time.sleep(0.5)
