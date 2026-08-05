"""
Génération des visuels d'analyse à partir des CSV produits par extraction_kpi.py.

Six figures sont écrites dans `../assets/` :
  1. apercu-kpi.png          — tableau d'indicateurs (image d'en-tête)
  2. cascade-resultats.png   — cascade des résultats du semestre
  3. seuil-rentabilite.png   — seuil de rentabilité et marge de sécurité
  4. rentabilite-produits.png— taux de marge et contribution par produit
  5. structure-bilan.png     — analyses verticale et horizontale du bilan
  6. previsions-ventes.png   — prévisions de ventes sur 36 mois

Palette : palette catégorielle validée pour la vision des couleurs
(écarts CVD ΔE >= 8 sur les paires adjacentes). Chaque série porte en plus
une étiquette directe, de sorte que la couleur n'est jamais le seul repère.

Usage :
    python graphiques.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE / "data"
DOSSIER_ASSETS = RACINE / "assets"

# --- Palette -------------------------------------------------------------
SURFACE = "#fcfcfb"
ENCRE = "#0b0b0b"
ENCRE_2 = "#52514e"
ENCRE_MUET = "#898781"
GRILLE = "#e1e0d9"
AXE = "#c3c2b7"

BLEU = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
JAUNE = "#eda100"
BLEU_PALE = "#9ec5f4"
BLEU_FONCE = "#184f95"

CRITIQUE = "#d03b3b"
ROUGE = "#e34948"
BON = "#0ca30c"

plt.rcParams.update(
    {
        # Sans cette option, une chaîne contenant deux « $ » (« T1 2,25 M$ · T2 2,65 M$ »)
        # est interprétée comme une formule mathématique par matplotlib.
        "text.parse_math": False,
        "font.family": "Arial",
        "font.size": 10,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": AXE,
        "axes.labelcolor": ENCRE_2,
        "text.color": ENCRE,
        "xtick.color": ENCRE_MUET,
        "ytick.color": ENCRE_MUET,
        "grid.color": GRILLE,
        "grid.linewidth": 0.8,
        "axes.grid": False,
        "savefig.facecolor": SURFACE,
    }
)


# --- Formatage des nombres (convention québécoise) -----------------------
MOINS = "−"  # signe moins typographique, plus lisible que le trait d'union


def dollars(valeur, decimales=0):
    """1234567.8 -> '1 234 568 $'"""
    texte = f"{abs(valeur):,.{decimales}f}".replace(","," ").replace(".", ",")
    return f"{MOINS if valeur < 0 else ''}{texte} $"


def millions(valeur, decimales=1):
    """12761706 -> '12,8 M$'"""
    texte = f"{abs(valeur) / 1e6:.{decimales}f} M$".replace(".", ",")
    return f"{MOINS if valeur < 0 else ''}{texte}"


def pourcent(valeur, decimales=1):
    """0.3594 -> '35,9 %'"""
    texte = f"{abs(valeur) * 100:.{decimales}f} %".replace(".", ",")
    return f"{MOINS if valeur < 0 else ''}{texte}"


def depouiller(ax, garder=("left", "bottom")):
    """Retire les bordures superflues et allège la grille."""
    for cote, epine in ax.spines.items():
        epine.set_visible(cote in garder)
        if cote in garder:
            epine.set_linewidth(0.8)
    ax.tick_params(length=0, labelsize=9)


def titrer(fig, titre, sous_titre=None, y=0.975):
    fig.text(0.012, y, titre, fontsize=15, fontweight="bold", color=ENCRE, va="top")
    if sous_titre:
        fig.text(
            0.012, y - 0.048, sous_titre, fontsize=10, color=ENCRE_2, va="top"
        )


def signer(fig, source="Source : bilan-demarrage.xlsx — Issa Ouedraogo"):
    fig.text(0.012, 0.012, source, fontsize=8, color=ENCRE_MUET)


# =========================================================================
# 1. Tableau d'indicateurs
# =========================================================================
def figure_kpi(ratios, seuil, scenarios, resultats):
    def res(nom, col):
        return resultats.loc[resultats["poste"] == nom, col].iloc[0]

    t1 = ratios.iloc[0]
    t2 = ratios.iloc[1]
    an1 = scenarios.loc[scenarios["scenario"] == "Prévisions année 1"].iloc[0]

    ventes_semestre = res("Ventes nettes", "cumul_semestre")
    resultat_semestre = res("Résultat net", "cumul_semestre")

    # (libellé, valeur, note, ton, sens)
    # « ton » donne la lecture (favorable / défavorable / simple niveau) et
    # pilote la couleur ; « sens » indique le mouvement réel T1 -> T2 et pilote
    # la flèche. Les deux sont indépendants : le levier financier MONTE (▲) et
    # c'est défavorable (rouge).
    tuiles = [
        ("Ventes du semestre", millions(ventes_semestre, 2),
         f"T1 {millions(res('Ventes nettes', 'trim_1'), 2)}  ·  "
         f"T2 {millions(res('Ventes nettes', 'trim_2'), 2)}", "neutre", None),
        ("Marge brute (T2)", pourcent(t2["marge_brute"]),
         f"{MOINS}{abs(t2['marge_brute'] - t1['marge_brute']) * 100:.1f}".replace(".", ",")
         + " points de pourcentage vs T1",
         "mauvais", "baisse"),
        ("Résultat net cumulé", dollars(resultat_semestre),
         f"soit {pourcent(resultat_semestre / ventes_semestre)} des ventes",
         "mauvais", None),
        ("Seuil de rentabilité", millions(seuil["seuil_rentabilite"], 2),
         "de ventes annuelles requises", "neutre", None),
        ("Marge de sécurité", pourcent(an1["taux_marge_securite"]),
         f"{millions(an1['marge_securite'], 2)} au-dessus du seuil", "bon", None),
        ("Frais fixes annuels", millions(seuil["frais_fixes_annuels"], 2),
         f"marge sur coût variable {pourcent(seuil['taux_marge_cout_variable'])}",
         "neutre", None),
        ("Liquidité générale (T2)", f"{t2['liquidite_generale']:.2f}".replace(".", ","),
         f"fonds de roulement {dollars(t2['fonds_roulement'])}", "mauvais", "baisse"),
        ("Levier financier (T2)", f"{t2['levier_financier']:.2f}".replace(".", ",") + " ×",
         f"endettement {pourcent(t2['endettement'])} de l'actif", "mauvais", "hausse"),
    ]

    couleurs = {"bon": BON, "mauvais": CRITIQUE, "neutre": BLEU_FONCE}
    fleches = {"hausse": "▲", "baisse": "▼", None: ""}

    fig = plt.figure(figsize=(12.6, 5.0))
    titrer(
        fig,
        "Bilan de démarrage — indicateurs clés du premier semestre",
        "Commerce de gros de caissons de rangement · 13 produits · exercice simulé sur 3 ans",
    )

    n_col, n_lig = 4, 2
    marge_g, marge_d = 0.012, 0.012
    haut, bas = 0.80, 0.09
    ecart_x, ecart_y = 0.016, 0.055
    larg = (1 - marge_g - marge_d - (n_col - 1) * ecart_x) / n_col
    haut_t = (haut - bas - (n_lig - 1) * ecart_y) / n_lig

    for i, (libelle, valeur, note, ton, sens) in enumerate(tuiles):
        col, lig = i % n_col, i // n_col
        x = marge_g + col * (larg + ecart_x)
        y = haut - haut_t - lig * (haut_t + ecart_y)

        fig.patches.append(
            FancyBboxPatch(
                (x, y), larg, haut_t,
                boxstyle="round,pad=0,rounding_size=0.012",
                transform=fig.transFigure, facecolor="#ffffff",
                edgecolor=GRILLE, linewidth=1.0, zorder=0,
            )
        )
        # Filet de couleur à gauche : redondant avec le repère ▲/▼ et le texte.
        fig.patches.append(
            plt.Rectangle(
                (x, y), 0.004, haut_t, transform=fig.transFigure,
                facecolor=couleurs[ton], edgecolor="none", zorder=1,
            )
        )
        fig.text(x + 0.018, y + haut_t - 0.045, libelle, fontsize=9.5, color=ENCRE_2)
        fig.text(
            x + 0.018, y + haut_t - 0.135,
            f"{fleches[sens]} {valeur}".strip(),
            fontsize=19, fontweight="bold", color=couleurs[ton], va="top",
        )
        fig.text(x + 0.018, y + 0.028, note, fontsize=8.5, color=ENCRE_MUET)

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "apercu-kpi.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 2. Cascade des résultats du semestre
# =========================================================================
def figure_cascade(resultats):
    def res(nom):
        return resultats.loc[resultats["poste"] == nom, "cumul_semestre"].iloc[0]

    ventes = res("Ventes nettes")
    cmv = res("Coût des marchandises vendues")
    total_frais = res("Total des frais d'exploitation")
    resultat = res("Résultat net")

    remuneration = res("Salaires") + res("Avantages sociaux") + res("Vacances")
    entretien = res("Entret./réparation")
    publicite = res("Publicité")
    loyer = res("Loyer")
    livraison = res("Frais de livraison")
    amortissements = sum(
        resultats.loc[
            resultats["poste"].str.startswith("Amort."), "cumul_semestre"
        ].fillna(0)
    )
    detailles = remuneration + entretien + publicite + loyer + livraison + amortissements
    autres = total_frais - detailles

    etapes = [
        ("Ventes nettes", ventes, "total"),
        ("Coût des\nmarchandises", -cmv, "retrait"),
        ("Rémunération", -remuneration, "retrait"),
        ("Entretien et\nréparation", -entretien, "retrait"),
        ("Publicité", -publicite, "retrait"),
        ("Loyer", -loyer, "retrait"),
        ("Livraison\nclients", -livraison, "retrait"),
        ("Amortissements", -amortissements, "retrait"),
        ("Autres frais", -autres, "retrait"),
        ("Perte nette", resultat, "total"),
    ]

    fig, ax = plt.subplots(figsize=(12.6, 5.6))
    fig.subplots_adjust(left=0.055, right=0.99, top=0.78, bottom=0.16)
    titrer(
        fig,
        "D'où vient la perte du premier semestre ?",
        "Décomposition des 4,90 M$ de ventes jusqu'au résultat net · cumul des trimestres 1 et 2",
    )

    cumul = 0.0
    for i, (libelle, montant, genre) in enumerate(etapes):
        if genre == "total":
            # Barre de total : elle part toujours de zéro, vers le haut si le
            # montant est positif, vers le bas s'il est négatif (la perte nette).
            base = min(0.0, montant)
            hauteur = abs(montant)
            couleur = BLEU if i == 0 else CRITIQUE
            cumul = montant if i == 0 else cumul
        else:
            base = cumul + montant
            hauteur = abs(montant)
            couleur = ROUGE
            cumul += montant

        ax.bar(i, hauteur, bottom=base, width=0.62, color=couleur,
               edgecolor=SURFACE, linewidth=2, zorder=3)

        etiquette = ("+" if i == 0 else "") + dollars(montant)
        if genre == "total" and montant < 0:
            ax.text(i, base - ventes * 0.022, etiquette, ha="center", va="top",
                    fontsize=9, fontweight="bold", color=couleur, zorder=4)
        else:
            ax.text(i, base + hauteur + ventes * 0.022, etiquette, ha="center",
                    va="bottom", fontsize=9, fontweight="bold",
                    color=couleur if genre == "total" else ENCRE, zorder=4)

        if i < len(etapes) - 1:
            ax.plot([i + 0.31, i + 1 - 0.31], [cumul, cumul], color=AXE,
                    linewidth=1, linestyle=(0, (3, 3)), zorder=2)

    ax.axhline(0, color=AXE, linewidth=1)
    ax.set_xticks(range(len(etapes)))
    ax.set_xticklabels([e[0] for e in etapes], fontsize=9, color=ENCRE_2)
    ax.set_yticks([0, 1e6, 2e6, 3e6, 4e6, 5e6])
    ax.set_yticklabels(["0", "1 M$", "2 M$", "3 M$", "4 M$", "5 M$"])
    ax.set_ylim(-0.6e6, 5.55e6)
    ax.yaxis.grid(True, zorder=0)
    depouiller(ax, garder=("bottom",))

    # Deux entrées seulement : la barre de perte nette est identifiée par son
    # étiquette d'axe et sa valeur, pas par une pastille de couleur proche du rouge
    # des charges.
    poignees = [
        plt.Rectangle((0, 0), 1, 1, color=BLEU),
        plt.Rectangle((0, 0), 1, 1, color=ROUGE),
    ]
    ax.legend(
        poignees, ["Ventes (+)", "Charges (−)"],
        loc="upper right", frameon=False, fontsize=9, ncol=2,
        bbox_to_anchor=(1.0, 1.10),
    )
    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "cascade-resultats.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 3. Seuil de rentabilité
# =========================================================================
def figure_seuil(seuil, scenarios):
    fixes = seuil["frais_fixes_annuels"]
    taux_var = seuil["taux_frais_variables"]
    point_mort = seuil["seuil_rentabilite"]
    an1 = scenarios.loc[scenarios["scenario"] == "Prévisions année 1"].iloc[0]

    x_max = 17e6
    xs = [0, x_max]
    ventes = xs
    couts = [fixes + taux_var * x for x in xs]

    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.76, bottom=0.13)
    titrer(
        fig,
        "Seuil de rentabilité : 10,88 M$ de ventes annuelles",
        "Les prévisions de l'année 1 dépassent le point mort de 1,88 M$ — une marge de sécurité de 14,8 %",
    )

    # Zone de perte / de profit délimitée par le croisement des deux droites.
    ax.fill_between(
        [0, point_mort], [0, point_mort], [fixes, fixes + taux_var * point_mort],
        color=ROUGE, alpha=0.09, zorder=1,
    )
    ax.fill_between(
        [point_mort, x_max], [point_mort, x_max],
        [fixes + taux_var * point_mort, fixes + taux_var * x_max],
        color=AQUA, alpha=0.12, zorder=1,
    )

    ax.plot(xs, ventes, color=BLEU, linewidth=2, zorder=4,
            label="Chiffre d'affaires")
    ax.plot(xs, couts, color=ORANGE, linewidth=2, zorder=4,
            label=f"Coûts totaux  (fixes + {pourcent(taux_var)} des ventes)")
    ax.plot(xs, [fixes, fixes], color=AQUA, linewidth=2,
            linestyle=(0, (5, 3)), zorder=4,
            label=f"Frais fixes annuels · {millions(fixes, 2)}")

    # Les deux droites se croisent : une étiquette posée le long d'une droite
    # oblique finit toujours par recouper l'autre droite. La légende, placée
    # dans la zone vide en haut à gauche, évite le problème.
    ax.legend(
        loc="upper left", frameon=False, fontsize=9.5,
        bbox_to_anchor=(0.015, 0.985), handlelength=2.2, labelspacing=0.7,
    )

    # Point mort
    ax.plot([point_mort], [point_mort], "o", markersize=10, color=ENCRE,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=6)
    ax.annotate(
        f"Point mort\n{millions(point_mort, 2)}",
        xy=(point_mort, point_mort), xytext=(point_mort + 0.6e6, point_mort - 2.6e6),
        fontsize=10, fontweight="bold", color=ENCRE, ha="center",
        arrowprops=dict(arrowstyle="-", color=ENCRE_MUET, linewidth=1),
        zorder=6,
    )

    # Prévisions année 1 et marge de sécurité
    prev = an1["ventes_requises"]
    ax.plot([prev, prev], [0, prev], color=ENCRE_MUET, linewidth=1,
            linestyle=(0, (2, 3)), zorder=3)
    ax.annotate(
        "", xy=(prev, 1.62e6), xytext=(point_mort, 1.62e6),
        arrowprops=dict(arrowstyle="<->", color=ENCRE, linewidth=1.2), zorder=6,
    )
    ax.text(
        (prev + point_mort) / 2, 1.45e6,
        f"Marge de sécurité\n{millions(an1['marge_securite'], 2)} ({pourcent(an1['taux_marge_securite'])})",
        ha="center", va="top", fontsize=9, fontweight="bold", color=ENCRE, zorder=6,
    )
    ax.text(prev, prev + 0.35e6, f"Prévisions année 1\n{millions(prev, 2)}",
            ha="center", va="bottom", fontsize=9, color=ENCRE_2, zorder=6)

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, x_max)
    graduations = [0, 4e6, 8e6, 12e6, 16e6]
    etiquettes = ["0", "4 M$", "8 M$", "12 M$", "16 M$"]
    ax.set_xticks(graduations)
    ax.set_xticklabels(etiquettes)
    ax.set_yticks(graduations)
    ax.set_yticklabels(etiquettes)
    ax.set_xlabel("Chiffre d'affaires annuel", fontsize=9.5)
    ax.set_ylabel("Dollars", fontsize=9.5)
    ax.grid(True, zorder=0)
    depouiller(ax)

    fig.text(
        0.075, 0.055,
        "Zone rouge : perte  ·  Zone verte : profit  ·  Frais fixes annualisés à partir du semestre 1 réel",
        fontsize=8.5, color=ENCRE_MUET,
    )
    signer(fig, "Source : bilan-demarrage.xlsx, feuille « Fx var et Fx fixe - Simul »")
    fig.savefig(DOSSIER_ASSETS / "seuil-rentabilite.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 4. Rentabilité par produit
# =========================================================================
def figure_produits(produits):
    df = produits.sort_values("taux_marge", ascending=True).reset_index(drop=True)
    y = range(len(df))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 6.2), sharey=True)
    fig.subplots_adjust(left=0.055, right=0.985, top=0.76, bottom=0.10, wspace=0.22)
    titrer(
        fig,
        "Rentabilité par produit : le plus vendu est le moins rentable",
        "P8 dégage la marge unitaire la plus faible (15,2 %) mais concentre 23,7 % de la marge totale du semestre",
    )

    # -- Panneau A : taux de marge sur coûts directs
    # Une seule teinte pour la série ; P8 est mis en évidence parce que le titre
    # et le sous-titre parlent explicitement de lui.
    couleurs = [CRITIQUE if p == "P8" else BLEU for p in df["produit"]]
    ax1.barh(y, df["taux_marge"], height=0.68, color=couleurs, zorder=3)
    for i, (t, p) in enumerate(zip(df["taux_marge"], df["marge_unitaire"])):
        ax1.text(t + 0.006, i, f"{pourcent(t)}   ({dollars(p, 2)}/u)",
                 va="center", fontsize=8.5, color=ENCRE_2, zorder=4)
    ax1.set_xlim(0, 0.46)
    ax1.set_xticks([0, 0.1, 0.2, 0.3])
    ax1.set_xticklabels(["0 %", "10 %", "20 %", "30 %"])
    ax1.set_title("Taux de marge sur coûts directs", fontsize=11,
                  fontweight="bold", color=ENCRE, loc="left", pad=10)
    ax1.xaxis.grid(True, zorder=0)
    depouiller(ax1, garder=("bottom",))

    # -- Panneau B : contribution à la marge totale (même ordre de produits)
    ax2.barh(y, df["part_marge_semestre"], height=0.68, color=ORANGE, zorder=3)
    for i, part in enumerate(df["part_marge_semestre"]):
        ax2.text(part + 0.005, i, pourcent(part), va="center",
                 fontsize=8.5, color=ENCRE_2, zorder=4)
    ax2.set_xlim(0, 0.30)
    ax2.set_xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25])
    ax2.set_xticklabels(["0 %", "5 %", "10 %", "15 %", "20 %", "25 %"])
    ax2.set_title("Part de la marge totale du semestre", fontsize=11,
                  fontweight="bold", color=ENCRE, loc="left", pad=10)
    ax2.xaxis.grid(True, zorder=0)
    depouiller(ax2, garder=("bottom",))

    ax1.set_yticks(list(y))
    ax1.set_yticklabels(df["produit"], fontsize=9.5, color=ENCRE)

    fig.text(
        0.055, 0.035,
        "Marge sur coûts directs = prix de vente − (coût d'achat + transport sur achat + commission "
        "+ avantages sociaux + livraison + honoraires).",
        fontsize=8.5, color=ENCRE_MUET,
    )
    signer(fig, "Source : bilan-demarrage.xlsx, feuille « S7 - Rentabilité par prod. »")
    fig.savefig(DOSSIER_ASSETS / "rentabilite-produits.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 5. Structure du bilan
# =========================================================================
def figure_bilan(bilans):
    def val(nom, col):
        return bilans.loc[bilans["poste"] == nom, col].iloc[0]

    actif_t1 = val("Total de l'actif", "trim_1")
    actif_t2 = val("Total de l'actif", "trim_2")

    composition = {
        "Actif — T1": [
            ("Actif à court terme", val("Total de l'actif à court terme", "trim_1") / actif_t1, BLEU),
            ("Immobilisations", val("Total des immobilisations", "trim_1") / actif_t1, BLEU_PALE),
        ],
        "Actif — T2": [
            ("Actif à court terme", val("Total de l'actif à court terme", "trim_2") / actif_t2, BLEU),
            ("Immobilisations", val("Total des immobilisations", "trim_2") / actif_t2, BLEU_PALE),
        ],
        "Financement — T1": [
            ("Passif à court terme", val("Total du passif à court terme", "trim_1") / actif_t1, ORANGE),
            ("Passif à long terme", val("Emprunt hypothécaire", "trim_1") / actif_t1, JAUNE),
            ("Capitaux propres", val("Total des capitaux propres", "trim_1") / actif_t1, AQUA),
        ],
        "Financement — T2": [
            ("Passif à court terme", val("Total du passif à court terme", "trim_2") / actif_t2, ORANGE),
            ("Passif à long terme", val("Emprunt hypothécaire", "trim_2") / actif_t2, JAUNE),
            ("Capitaux propres", val("Total des capitaux propres", "trim_2") / actif_t2, AQUA),
        ],
    }

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.6, 5.8), gridspec_kw={"width_ratios": [1.05, 1]}
    )
    fig.subplots_adjust(left=0.115, right=0.985, top=0.75, bottom=0.22, wspace=0.32)
    titrer(
        fig,
        "Structure du bilan : un financement qui repose sur le court terme",
        "Analyse verticale (% de l'actif total) et variation d'un trimestre à l'autre",
    )

    # -- Panneau A : analyse verticale
    etiquettes = list(composition.keys())
    for i, cle in enumerate(etiquettes):
        gauche = 0.0
        for nom, part, couleur in composition[cle]:
            ax1.barh(i, part, left=gauche, height=0.6, color=couleur,
                     edgecolor=SURFACE, linewidth=2, zorder=3)
            if part > 0.06:
                ax1.text(gauche + part / 2, i, pourcent(part, 0), ha="center",
                         va="center", fontsize=9, fontweight="bold",
                         color="#ffffff" if couleur in (BLEU, ORANGE) else ENCRE,
                         zorder=4)
            gauche += part

    ax1.set_yticks(range(len(etiquettes)))
    ax1.set_yticklabels(etiquettes, fontsize=9.5, color=ENCRE)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 1)
    ax1.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax1.set_xticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"])
    ax1.set_title("Analyse verticale", fontsize=11, fontweight="bold",
                  color=ENCRE, loc="left", pad=10)
    depouiller(ax1, garder=("bottom",))

    poignees = [
        plt.Rectangle((0, 0), 1, 1, color=c)
        for c in (BLEU, BLEU_PALE, ORANGE, JAUNE, AQUA)
    ]
    ax1.legend(
        poignees,
        ["Actif à court terme", "Immobilisations", "Passif à court terme",
         "Passif à long terme", "Capitaux propres"],
        loc="upper left", bbox_to_anchor=(0, -0.12), frameon=False,
        fontsize=9, ncol=3, handlelength=1.1, handleheight=1.1,
        columnspacing=1.2,
    )

    # -- Panneau B : analyse horizontale
    postes = [
        "Comptes fournisseurs", "Comptes clients", "Banque",
        "Stocks de marchandises", "Taxes à payer", "Total de l'actif",
    ]
    sous_ensemble = (
        bilans[bilans["poste"].isin(postes)]
        .set_index("poste")
        .loc[postes]
        .reset_index()
        .sort_values("ah_t1_t2")
    )
    couleurs = [ROUGE if v < 0 else BLEU for v in sous_ensemble["ah_t1_t2"]]
    positions = range(len(sous_ensemble))
    ax2.barh(positions, sous_ensemble["ah_t1_t2"], height=0.62,
             color=couleurs, zorder=3)
    for i, v in enumerate(sous_ensemble["ah_t1_t2"]):
        decalage = 0.03 if v >= 0 else -0.03
        ax2.text(v + decalage, i, f"{'+' if v >= 0 else '−'}{pourcent(abs(v))}",
                 va="center", ha="left" if v >= 0 else "right",
                 fontsize=9, fontweight="bold", color=ENCRE, zorder=4)

    ax2.set_yticks(list(positions))
    ax2.set_yticklabels(sous_ensemble["poste"], fontsize=9.5, color=ENCRE)
    ax2.axvline(0, color=AXE, linewidth=1, zorder=2)
    ax2.set_xlim(-1.18, 0.75)
    ax2.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5])
    ax2.set_xticklabels(["−75 %", "−50 %", "−25 %", "0 %", "+25 %", "+50 %"])
    ax2.set_title("Analyse horizontale · variation T1 → T2", fontsize=11,
                  fontweight="bold", color=ENCRE, loc="left", pad=10)
    ax2.xaxis.grid(True, zorder=0)
    depouiller(ax2, garder=("bottom",))

    signer(fig, "Source : bilan-demarrage.xlsx, feuilles « S6 Bilan TRIM 1 » et « S8 Bilan TRIM 2 »")
    fig.savefig(DOSSIER_ASSETS / "structure-bilan.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 6. Prévisions de ventes sur 36 mois
# =========================================================================
def figure_previsions(previsions):
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    fig.subplots_adjust(left=0.065, right=0.985, top=0.76, bottom=0.15)
    titrer(
        fig,
        "Prévisions de ventes sur 36 mois : montée en charge puis vitesse de croisière",
        "Les creux correspondent aux produits saisonniers, absents des trimestres 2 et 3",
    )

    x = previsions["mois_absolu"]
    y = previsions["ventes"]

    ax.fill_between(x, y, color=BLEU, alpha=0.10, zorder=2)
    ax.plot(x, y, color=BLEU, linewidth=2, zorder=4)

    for annee in (2, 3):
        ax.axvline((annee - 1) * 12 + 0.5, color=AXE, linewidth=1,
                   linestyle=(0, (3, 3)), zorder=1)

    totaux = previsions.groupby("annee")["ventes"].sum()
    for annee, total in totaux.items():
        ax.text(
            (annee - 1) * 12 + 6.5, 1.86e6,
            f"Année {annee} · {millions(total, 1)}",
            ha="center", fontsize=10, fontweight="bold", color=ENCRE_2, zorder=5,
        )

    # Repères : montée en charge et point le plus haut
    haut = previsions.loc[previsions["ventes"].idxmax()]
    ax.plot([haut["mois_absolu"]], [haut["ventes"]], "o", markersize=9,
            color=BLEU, markeredgecolor=SURFACE, markeredgewidth=2, zorder=6)
    ax.annotate(
        f"Sommet · {millions(haut['ventes'], 2)}\n(mois {int(haut['mois'])} de l'année {int(haut['annee'])})",
        xy=(haut["mois_absolu"] - 0.15, haut["ventes"] - 0.03e6),
        xytext=(haut["mois_absolu"] - 4.2, 1.50e6),
        fontsize=9, color=ENCRE, ha="center", va="center",
        arrowprops=dict(arrowstyle="-", color=ENCRE_MUET, linewidth=1), zorder=6,
    )
    debut = previsions.iloc[0]
    ax.annotate(
        f"Démarrage · {millions(debut['ventes'], 2)}",
        xy=(1, debut["ventes"]), xytext=(2.4, debut["ventes"] - 0.30e6),
        fontsize=9, color=ENCRE_2, ha="left",
        arrowprops=dict(arrowstyle="-", color=ENCRE_MUET, linewidth=1), zorder=6,
    )

    ax.set_xlim(0.5, 36.5)
    ax.set_ylim(0, 2.05e6)
    ax.set_xticks([1, 6, 12, 18, 24, 30, 36])
    ax.set_xticklabels(["Mois 1", "6", "12", "18", "24", "30", "36"])
    ax.set_yticks([0, 0.5e6, 1e6, 1.5e6, 2e6])
    ax.set_yticklabels(["0", "0,5 M$", "1,0 M$", "1,5 M$", "2,0 M$"])
    ax.set_ylabel("Ventes mensuelles", fontsize=9.5)
    ax.yaxis.grid(True, zorder=0)
    depouiller(ax, garder=("bottom",))

    signer(fig, "Source : bilan-demarrage.xlsx, feuille « S1 - projections »")
    fig.savefig(DOSSIER_ASSETS / "previsions-ventes.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
def main():
    DOSSIER_ASSETS.mkdir(exist_ok=True)

    lire = lambda nom: pd.read_csv(DOSSIER_DONNEES / nom)
    resultats = lire("etats_resultats.csv")
    bilans = lire("bilans.csv")
    ratios = lire("ratios.csv")
    scenarios = lire("seuil_scenarios.csv")
    produits = lire("rentabilite_produits.csv")
    previsions = lire("previsions_ventes.csv")
    seuil = lire("seuil_synthese.csv").iloc[0]

    figures = [
        ("apercu-kpi.png", lambda: figure_kpi(ratios, seuil, scenarios, resultats)),
        ("cascade-resultats.png", lambda: figure_cascade(resultats)),
        ("seuil-rentabilite.png", lambda: figure_seuil(seuil, scenarios)),
        ("rentabilite-produits.png", lambda: figure_produits(produits)),
        ("structure-bilan.png", lambda: figure_bilan(bilans)),
        ("previsions-ventes.png", lambda: figure_previsions(previsions)),
    ]
    for nom, tracer in figures:
        tracer()
        print(f"  {nom}")

    print(f"\n{len(figures)} figures écrites dans {DOSSIER_ASSETS}")


if __name__ == "__main__":
    main()
