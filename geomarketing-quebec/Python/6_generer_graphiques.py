"""
Génère les visualisations complémentaires (au-delà du classement déjà produit par
5_analyse_marche.py) à partir de data/synthese_regions.csv : positionnement
population/revenu et indice de concurrence par région (zones sous-exploitées vs saturées).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_DIR / "synthese_regions.csv")
top3 = set(df.nlargest(3, "score_opportunite")["nom_region"])
couleurs = ["#B96A20" if r in top3 else "#1E6E8C" for r in df["nom_region"]]

# --- Positionnement population x revenu disponible (taille = score) ---
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.scatter(
    df["population_totale"], df["revenu_disponible_habitant"],
    s=df["score_opportunite"] * 8, c=couleurs, alpha=0.8, edgecolors="white", linewidths=0.8,
)
for _, row in df.iterrows():
    label = row["nom_region"] if row["nom_region"] in top3 or row["population_totale"] > 400000 else None
    if label:
        ax.annotate(label, (row["population_totale"], row["revenu_disponible_habitant"]),
                    xytext=(6, 6), textcoords="offset points", fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("Population totale (échelle log)")
ax.set_ylabel("Revenu disponible par habitant ($)")
ax.set_title("Positionnement des régions — population vs revenu disponible\n(taille du point = score d'opportunité)")
fig.tight_layout()
fig.savefig(ASSETS_DIR / "positionnement-population-revenu.png", dpi=150)
plt.close(fig)

# --- Indice de concurrence (zones sous-exploitées vs saturées) ---
df_tri = df.sort_values("indice_concurrence")
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(df_tri["nom_region"], df_tri["indice_concurrence"], color="#1E6E8C")
ax.set_xlabel("Indice de concurrence (établissements / habitant)")
ax.set_title("Intensité concurrentielle par région\n(en haut = marché moins saturé, en bas = plus de concurrence par habitant)")
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(ASSETS_DIR / "indice-concurrence.png", dpi=150)
plt.close(fig)

print("Graphiques écrits dans", ASSETS_DIR)
