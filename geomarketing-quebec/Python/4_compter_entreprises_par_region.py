"""
Compte le nombre d'établissements par région administrative à partir du registre des
entreprises du Québec (data/entreprises_raw.zip, téléchargé par 1_telecharger_entreprises.py).

Le fichier Etablissements.csv du registre donne une adresse municipale (ville), pas de code
de région administrative directement. On rattache donc chaque ville à sa région via le
dictionnaire ville_region.py (les ~500 municipalités les plus fréquentes, couvrant ~90% des
établissements). Les villes absentes du dictionnaire sont comptées comme "non classées" et
exclues du calcul — la couverture réelle obtenue est d'environ 81%, imprimée à l'écran.
L'indice de concurrence (analyse 3) est donc une estimation, pas un dénombrement exhaustif.
"""

import csv
import io
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ville_region import VILLE_REGION

ZIP_PATH = Path(__file__).resolve().parent.parent / "data" / "entreprises_raw.zip"

region_counts = Counter()
non_classe = 0
total = 0

z = zipfile.ZipFile(ZIP_PATH)
with z.open("Etablissements.csv") as fbin:
    f = io.TextIOWrapper(fbin, encoding="utf-8-sig", errors="replace")
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        addr = row.get("LIGN2_ADR", "") or ""
        m = re.match(r"^(.*?)\s*\(Qu[eé]bec\)\s*$", addr.strip(), re.IGNORECASE)
        city = (m.group(1).strip() if m else addr.strip()).upper()
        region = VILLE_REGION.get(city)
        if region:
            region_counts[region] += 1
        else:
            non_classe += 1

print(f"Total établissements : {total}")
print(f"Non classés (ville hors dictionnaire) : {non_classe} ({100*non_classe/total:.1f}%)")
print()
for region, n in sorted(region_counts.items(), key=lambda x: -x[1]):
    print(f"{region:35s} {n:8d}")

out = Path(__file__).resolve().parent.parent / "data" / "entreprises_regions.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.writer(fo)
    w.writerow(["nom_region", "nb_entreprises"])
    for region, n in sorted(region_counts.items()):
        w.writerow([region, n])
print(f"\nÉcrit : {out}")
