"""
Parse les fiches HTML téléchargées par 2_scraper_isq_regions.py et en extrait, pour
chaque région, l'édition la plus récente disponible pour chaque indicateur (population,
croissance, revenu disponible, chômage — chacun a sa propre année de référence). Écrit
data/isq_regions.csv, consommé ensuite par 5_analyse_marche.py.
"""

import csv
import html as htmlmod
import re
from pathlib import Path

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

RAW = Path(__file__).resolve().parent.parent / "data" / "raw_isq"


def clean_num(s):
    s = s.strip().replace(" ", "").replace(",", ".")
    return float(s)


def split_editions(text):
    text = htmlmod.unescape(text).replace("\xa0", " ")
    parts = re.split(r'<span class="collapsible-title">\s*[ÉE]dition\s*(\d{4})\s*</span>', text)
    editions = []
    for i in range(1, len(parts), 2):
        editions.append((parts[i], parts[i + 1]))
    return editions


def find_population(content):
    # Format A (newest editions): "Population totale : <strong>448 665 </strong>au 1er juillet 2023"
    m = re.search(
        r"Population totale\s*:\s*<strong>\s*([\d.,\s]+?)\s*</strong>\s*au\s*1<sup>er</sup>\s*juillet\s*(\d{4})",
        content,
    )
    if m:
        return clean_num(m.group(1)), int(m.group(2))
    # Format B (older editions): "Population totale (1er juillet 2022) : <strong>444 072</strong>"
    m = re.search(
        r"Population totale\s*\(1<sup>er</sup>\s*juillet\s*(\d{4})\)\s*:\s*<strong>\s*([\d.,\s]+?)\s*</strong>",
        content,
    )
    if m:
        return clean_num(m.group(2)), int(m.group(1))
    return None


def find_simple(content, label, unit_suffix):
    pattern = rf"{label}[^<]*?\((\d{{4}})\)[^<]*?:\s*<strong>\s*([\d.,\s]+?)\s*{unit_suffix}\s*</strong>"
    m = re.search(pattern, content)
    if not m:
        return None
    return clean_num(m.group(2)), int(m.group(1))


def find_growth(content):
    m = re.search(r"taux d'accroissement annuel[^<]*?(\d+[.,]\d+)\s*(pour mille|%)", content)
    if not m:
        return None
    val = clean_num(m.group(1))
    if m.group(2) == "pour mille":
        val = val / 10
    return round(val, 2)


results = []
for slug, nom in REGIONS:
    text = (RAW / f"{slug}.html").read_text(encoding="utf-8")
    editions = split_editions(text)
    pop = pop_year = revenu = revenu_year = chomage = chomage_year = croissance = None

    for year, content in editions:
        if pop is None:
            r = find_population(content)
            if r:
                pop, pop_year = r
                croissance = find_growth(content)
        if revenu is None:
            r = find_simple(content, r"Revenu disponible par habitant", r"\$")
            if r:
                revenu, revenu_year = r
        if chomage is None:
            r = find_simple(content, r"Taux de chômage[^<]*", r"%")
            if r:
                chomage, chomage_year = r

    results.append({
        "nom_region": nom,
        "population_totale": pop,
        "annee_population": pop_year,
        "croissance_pct_annuelle": croissance,
        "revenu_disponible_habitant": revenu,
        "annee_revenu": revenu_year,
        "taux_chomage": chomage,
        "annee_chomage": chomage_year,
    })

out = Path(__file__).resolve().parent.parent / "data" / "isq_regions.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)

missing = 0
for r in results:
    vals = {k: v for k, v in r.items() if k != "nom_region"}
    if any(v is None for v in vals.values()):
        missing += 1
    print(r["nom_region"], "->", vals)
print(f"\n{missing}/{len(results)} régions avec au moins un champ manquant")
