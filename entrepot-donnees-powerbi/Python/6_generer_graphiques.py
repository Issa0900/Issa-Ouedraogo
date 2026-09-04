"""
6_generer_graphiques.py — Apercus visuels des pages du rapport.

Ces images ne sont PAS des captures de Power BI : ce sont des reconstitutions
matplotlib des memes pages, alimentees par les memes requetes SQL (celles de
SQL/2_requetes_analyse.sql, rechargees ici par leur marqueur). Les chiffres
affiches sont donc exactement ceux du rapport, pas une illustration approximative.

Palette alignee sur celle du portfolio (assets/css/site.css).

Sortie : assets/*.png
"""

from __future__ import annotations

import os
import re
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "data", "entrepot", "boreal.db")
REQUETES = os.path.join(BASE, "SQL", "2_requetes_analyse.sql")
ASSETS = os.path.join(BASE, "assets")
os.makedirs(ASSETS, exist_ok=True)

PAPIER = "#f1f2ec"
PAPIER2 = "#e8eae1"
ENCRE = "#1a1e17"
ENCRE_DOUCE = "#535a4c"
ACCENT = "#0b6b45"
ALERTE = "#a8432f"
NEUTRE = "#9aa290"

plt.rcParams.update({
    "figure.facecolor": PAPIER, "axes.facecolor": PAPIER,
    "savefig.facecolor": PAPIER, "text.color": ENCRE,
    "axes.labelcolor": ENCRE_DOUCE, "xtick.color": ENCRE_DOUCE,
    "ytick.color": ENCRE_DOUCE, "axes.edgecolor": "#c9ccc0",
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#d8dbd0", "grid.linewidth": 0.7,
    # Sans cela, deux symboles "$" dans une meme chaine sont interpretes comme une
    # formule LaTeX et le rendu echoue. Aucune formule mathematique ici.
    "text.parse_math": False,
})

cx = sqlite3.connect(DB)
cx.row_factory = sqlite3.Row

with open(REQUETES, encoding="utf-8") as f:
    contenu = f.read()
blocs, nom, courant = {}, None, []
for ligne in contenu.splitlines():
    m = re.match(r"^--\s*@(\w+)\s*$", ligne)
    if m:
        if nom:
            blocs[nom] = "\n".join(courant)
        nom, courant = m.group(1), []
    elif nom is not None:
        courant.append(ligne)
if nom:
    blocs[nom] = "\n".join(courant)

req = lambda cle: [dict(r) for r in cx.execute(blocs[cle])]

espace = lambda v: f"{v:,.0f}".replace(",", " ")
fmt_M = FuncFormatter(lambda v, _: f"{v/1e6:.1f} M$".replace(".", ","))
fmt_k = FuncFormatter(lambda v, _: f"{v/1e3:.0f} k$")


def titrer(fig, titre: str, sous_titre: str) -> None:
    fig.text(0.012, 0.965, titre, fontsize=15, fontweight="bold", va="top",
             fontfamily="DejaVu Serif")
    fig.text(0.012, 0.918, sous_titre, fontsize=9.5, color=ENCRE_DOUCE, va="top")
    fig.text(0.012, 0.018, "Boréal Distribution (données fictives) — reconstitution du "
             "rapport Power BI à partir des mêmes requêtes SQL",
             fontsize=7.5, color=NEUTRE)


def enregistrer(fig, nom_fichier: str) -> None:
    chemin = os.path.join(ASSETS, nom_fichier)
    fig.savefig(chemin, dpi=150, bbox_inches="tight", pad_inches=0.32)
    plt.close(fig)
    print(f"  {nom_fichier}  ({os.path.getsize(chemin)/1024:.0f} Ko)")


# =============================================================================
# 1. Vue direction
# =============================================================================
resultat = {r["annee"]: r for r in req("resultat_par_annee")}
saison = req("saisonnalite")
familles = req("marge_par_famille")

fig = plt.figure(figsize=(13, 7.4))
titrer(fig, "Page 1 — Vue direction",
       "Le chiffre d'affaires progresse de 17,7 %. La marge brute perd 3,9 points. "
       "Les deux lectures ne racontent pas la même histoire.")

# --- bandeau d'indicateurs ---
r24, r25 = resultat[2024], resultat[2025]
indicateurs = [
    ("Chiffre d'affaires 2025", f"{espace(r25['ca'])} $",
     f"+{100*(r25['ca']/r24['ca']-1):.1f} % vs 2024".replace(".", ","), ACCENT),
    ("Taux de marge brute", f"{r25['marge_brute_pct']:.1f} %".replace(".", ","),
     f"{r25['marge_brute_pct']-r24['marge_brute_pct']:+.1f} pts vs 2024".replace(".", ","), ALERTE),
    ("Résultat d'exploitation", f"{espace(r25['resultat_exploitation'])} $",
     f"{r25['resultat_pct']:.1f} % du CA".replace(".", ","), ENCRE),
    ("Panier moyen", f"{espace(r25['panier_moyen'])} $",
     f"{r25['nb_commandes']} commandes", ENCRE),
]
for i, (libelle, valeur, note, couleur) in enumerate(indicateurs):
    ax = fig.add_axes([0.012 + i * 0.2485, 0.685, 0.232, 0.175])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               facecolor=PAPIER2, edgecolor="#d3d6cb", linewidth=0.8))
    ax.text(0.06, 0.76, libelle.upper(), fontsize=7.6, color=ENCRE_DOUCE,
            transform=ax.transAxes)
    ax.text(0.06, 0.40, valeur, fontsize=18, fontweight="bold", color=ENCRE,
            transform=ax.transAxes)
    ax.text(0.06, 0.15, note, fontsize=8.6, color=couleur, fontweight="bold",
            transform=ax.transAxes)

# --- courbe mensuelle ---
ax1 = fig.add_axes([0.055, 0.10, 0.44, 0.50])
mois = [s["nom_mois"][:4].capitalize() for s in saison]
ax1.plot(mois, [s["ca_2024"] for s in saison], marker="o", ms=4.5, lw=2,
         color=NEUTRE, label="2024")
ax1.plot(mois, [s["ca_2025"] for s in saison], marker="o", ms=4.5, lw=2.4,
         color=ACCENT, label="2025")
ax1.set_title("Chiffre d'affaires mensuel")
ax1.yaxis.set_major_formatter(fmt_M)
ax1.grid(axis="y", alpha=0.6)
ax1.set_axisbelow(True)
ax1.legend(frameon=False, fontsize=9, loc="upper left")
ax1.tick_params(axis="x", labelrotation=45, labelsize=8.5)
ax1.annotate("Pic d'approvisionnement\navant la saison hiver", xy=(7.85, saison[8]["ca_2025"]),
             xytext=(2.9, saison[8]["ca_2025"] * 0.86), fontsize=8, color=ENCRE_DOUCE,
             arrowprops=dict(arrowstyle="->", color=NEUTRE, lw=0.9,
                             connectionstyle="arc3,rad=-0.15"))

# --- marge par famille ---
ax2 = fig.add_axes([0.575, 0.10, 0.41, 0.50])
noms = [f["famille"] for f in familles][::-1]
y = range(len(noms))
v24 = [f["marge_2024_pct"] for f in familles][::-1]
v25 = [f["marge_2025_pct"] for f in familles][::-1]
ax2.barh([i + 0.20 for i in y], v24, height=0.38, color=NEUTRE, label="2024")
ax2.barh([i - 0.20 for i in y], v25, height=0.38,
         color=[ALERTE if a - b > 5 else ACCENT for a, b in zip(v24, v25)], label="2025")
ax2.set_yticks(list(y))
ax2.set_yticklabels(noms, fontsize=9)
ax2.set_title("Taux de marge brute par famille (%)")
ax2.grid(axis="x", alpha=0.6)
ax2.set_axisbelow(True)
ax2.legend(frameon=False, fontsize=9, loc="upper right")
# L'ecart vient de la requete, pas d'une soustraction de valeurs deja arrondies :
# 25,5 - 35,5 donnerait -10,0 pts la ou l'ecart reel est de -9,9 pts.
ecarts = [f["variation_points"] for f in familles][::-1]
for i, (a, b, e) in enumerate(zip(v24, v25, ecarts)):
    ax2.text(b + 0.5, i - 0.20, f"{e:+.1f}".replace(".", ",") + " pts", va="center",
             fontsize=7.8, color=ALERTE if a - b > 5 else ENCRE_DOUCE, fontweight="bold")
ax2.set_xlim(0, max(v24 + v25) * 1.22)
enregistrer(fig, "01-vue-direction.png")


# =============================================================================
# 2. Origine de la perte de marge
# =============================================================================
fournisseurs = req("cout_achat_par_fournisseur")
manque = req("impact_chiffre_derive")

fig = plt.figure(figsize=(13, 6.2))
titrer(fig, "Page 2 — D'où vient la perte de marge",
       "Le prix de vente n'a pas bougé : c'est le coût d'achat d'un fournisseur qui a "
       "dérivé. La jointure vente → article → fournisseur est ce qui le révèle.")

ax1 = fig.add_axes([0.055, 0.13, 0.40, 0.68])
f8 = fournisseurs[:8][::-1]
noms = [f["fournisseur"] for f in f8]
var = [f["variation_cout_pct"] for f in f8]
couleurs = [ALERTE if v > 8 else (ACCENT if v < 3 else NEUTRE) for v in var]
ax1.barh(range(len(f8)), var, color=couleurs, height=0.62)
ax1.set_yticks(range(len(f8)))
ax1.set_yticklabels(noms, fontsize=9)
ax1.set_title("Variation du coût d'achat unitaire, 2025 vs 2024 (%)")
ax1.grid(axis="x", alpha=0.6)
ax1.set_axisbelow(True)
ax1.axvline(0, color="#c9ccc0", lw=1)
for i, v in enumerate(var):
    # Une etiquette negative posee a droite de sa barre chevaucherait l'axe :
    # on la bascule a gauche, alignee a droite.
    decalage, alignement = (0.35, "left") if v >= 0 else (-0.35, "right")
    ax1.text(v + decalage, i, f"{v:+.1f}".replace(".", ",") + " %", va="center",
             ha=alignement, fontsize=8.4, fontweight="bold",
             color=ALERTE if v > 8 else ENCRE_DOUCE)
ax1.set_xlim(min(var) - 2.2, max(var) * 1.28)

ax2 = fig.add_axes([0.575, 0.13, 0.41, 0.68])
m5 = manque[:5][::-1]
noms2 = [m["fournisseur"] for m in m5]
val = [m["manque_a_gagner"] for m in m5]
ax2.barh(range(len(m5)), val, height=0.62,
         color=[ALERTE if v > 100000 else NEUTRE for v in val])
ax2.set_yticks(range(len(m5)))
ax2.set_yticklabels(noms2, fontsize=9)
ax2.set_title("Marge perdue en 2025 si le coût d'achat était resté à son niveau 2024")
ax2.xaxis.set_major_formatter(fmt_k)
ax2.grid(axis="x", alpha=0.6)
ax2.set_axisbelow(True)
for i, v in enumerate(val):
    ax2.text(v * 1.03, i, espace(v) + " $", va="center", fontsize=8.6,
             fontweight="bold", color=ALERTE if v > 100000 else ENCRE_DOUCE)
ax2.set_xlim(0, max(val) * 1.34)
principal = manque[0]
part = 100 * principal["manque_a_gagner"] / resultat[2025]["resultat_exploitation"]
ax2.text(0.5, -0.19,
         f"À lui seul, {principal['fournisseur']} représente "
         f"{espace(principal['manque_a_gagner'])} $ de marge perdue, soit "
         f"{part:.0f} % du résultat d'exploitation de l'exercice.",
         transform=ax2.transAxes, ha="center", fontsize=8.8, color=ENCRE,
         fontweight="bold")
enregistrer(fig, "02-origine-perte-marge.png")


# =============================================================================
# 3. Rotation des stocks
# =============================================================================
rotation = [r for r in req("rotation_stock") if r["annee"] == 2025]
rotation.sort(key=lambda r: r["rotation"])

fig = plt.figure(figsize=(13, 5.2))
bas, haut = rotation[0], rotation[-1]
part_ventes = 100 * bas["cout_marchandises_vendues"] / haut["cout_marchandises_vendues"]
titrer(fig, "Page 4 — Rotation des stocks par entrepôt",
       f"{bas['entrepot']} immobilise {espace(bas['stock_moyen'])} $ de marchandise pour "
       f"{part_ventes:.0f} % des ventes de {haut['entrepot']}, qui en immobilise "
       f"{espace(haut['stock_moyen'])} $ : {bas['jours_de_stock']:.0f} jours de stock "
       f"contre {haut['jours_de_stock']:.0f}.")

ax1 = fig.add_axes([0.055, 0.15, 0.26, 0.62])
noms = [r["entrepot"] for r in rotation]
rot = [r["rotation"] for r in rotation]
ax1.bar(noms, rot, color=[ALERTE if v < 3.5 else ACCENT for v in rot], width=0.56)
ax1.set_title("Rotation annuelle (fois)")
ax1.grid(axis="y", alpha=0.6)
ax1.set_axisbelow(True)
for i, v in enumerate(rot):
    ax1.text(i, v + 0.14, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9.5,
             fontweight="bold", color=ENCRE)
ax1.set_ylim(0, max(rot) * 1.2)

ax2 = fig.add_axes([0.385, 0.15, 0.26, 0.62])
jours = [r["jours_de_stock"] for r in rotation]
ax2.bar(noms, jours, color=[ALERTE if v > 100 else ACCENT for v in jours], width=0.56)
ax2.set_title("Jours de stock")
ax2.grid(axis="y", alpha=0.6)
ax2.set_axisbelow(True)
for i, v in enumerate(jours):
    ax2.text(i, v + 4, f"{v:.0f} j", ha="center", fontsize=9.5, fontweight="bold", color=ENCRE)
ax2.set_ylim(0, max(jours) * 1.2)

ax3 = fig.add_axes([0.715, 0.15, 0.27, 0.62])
stock = [r["stock_moyen"] for r in rotation]
ax3.bar(noms, stock, color=NEUTRE, width=0.56)
ax3.set_title("Stock moyen immobilisé")
ax3.yaxis.set_major_formatter(fmt_k)
ax3.grid(axis="y", alpha=0.6)
ax3.set_axisbelow(True)
for i, v in enumerate(stock):
    ax3.text(i, v * 1.02, espace(v) + " $", ha="center", fontsize=8.6,
             fontweight="bold", color=ENCRE)
ax3.set_ylim(0, max(stock) * 1.18)
enregistrer(fig, "03-rotation-stocks.png")


# =============================================================================
# 4. Concentration clients (Pareto)
# =============================================================================
top = req("concentration_clients")

fig = plt.figure(figsize=(12, 5.6))
nb_clients = cx.execute("SELECT COUNT(*) FROM dim_client").fetchone()[0]
titrer(fig, "Page 3 — Concentration du chiffre d'affaires",
       f"Sur {nb_clients} clients actifs, les 10 premiers pèsent "
       f"{top[-1]['part_cumulee_pct']:.1f} % du chiffre d'affaires — et le premier "
       f"{top[0]['part_pct']:.1f} % à lui seul.".replace(".", ","))

ax = fig.add_axes([0.075, 0.20, 0.86, 0.60])
noms = [t["nom"] for t in top]
ca = [t["ca"] for t in top]
ax.bar(range(len(top)), ca, color=ACCENT, width=0.62)
ax.set_xticks(range(len(top)))
ax.set_xticklabels(noms, rotation=28, ha="right", fontsize=8.5)
ax.yaxis.set_major_formatter(fmt_M)
ax.grid(axis="y", alpha=0.6)
ax.set_axisbelow(True)
ax.set_title("Chiffre d'affaires cumulé 2024-2025, 10 premiers clients")

ax2 = ax.twinx()
cum = [t["part_cumulee_pct"] for t in top]
ax2.plot(range(len(top)), cum, color=ALERTE, marker="o", ms=5, lw=2)
ax2.set_ylim(0, 40)
ax2.set_ylabel("Part cumulée du CA total (%)", color=ALERTE, fontsize=9)
ax2.tick_params(axis="y", colors=ALERTE)
ax2.spines["right"].set_visible(True)
ax2.spines["right"].set_color("#c9ccc0")
for i, v in enumerate(cum):
    if i % 3 == 0 or i == len(cum) - 1:
        ax2.text(i, v + 1.6, f"{v:.1f} %".replace(".", ","), ha="center", fontsize=8,
                 color=ALERTE, fontweight="bold")
enregistrer(fig, "04-concentration-clients.png")


# =============================================================================
# 5. Qualite des donnees
# =============================================================================
qualite = req("qualite_donnees")
qualite.sort(key=lambda r: r["total"])

fig = plt.figure(figsize=(12, 6.4))
total_rejet = sum(q["lignes_rejetees"] for q in qualite)
total_corr = sum(q["valeurs_traitees"] for q in qualite)
titrer(fig, "Page 6 — Qualité des données",
       f"{total_rejet} lignes écartées et {total_corr} valeurs corrigées, chacune "
       f"tracée avec sa valeur d'origine. Rien n'est supprimé en silence.")

ax = fig.add_axes([0.20, 0.10, 0.76, 0.72])
noms = [q["motif"].replace("_", " ") for q in qualite]
rej = [q["lignes_rejetees"] for q in qualite]
cor = [q["valeurs_traitees"] for q in qualite]
y = range(len(qualite))
ax.barh(y, rej, color=ALERTE, height=0.62, label="Ligne rejetée")
ax.barh(y, cor, left=rej, color=ACCENT, height=0.62, label="Valeur corrigée ou signalée")
ax.set_yticks(list(y))
ax.set_yticklabels(noms, fontsize=9)
ax.grid(axis="x", alpha=0.6)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=9, loc="lower right")
ax.set_title("Nature des anomalies rencontrées par l'ETL")
for i, q in enumerate(qualite):
    ax.text(q["total"] + 8, i, str(q["total"]), va="center", fontsize=8.4,
            fontweight="bold", color=ENCRE_DOUCE)
ax.set_xlim(0, max(q["total"] for q in qualite) * 1.13)
enregistrer(fig, "05-qualite-donnees.png")

print("\nApercus generes dans assets/")
cx.close()
