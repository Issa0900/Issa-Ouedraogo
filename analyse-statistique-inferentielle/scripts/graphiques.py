"""
Génération des visuels d'analyse à partir des CSV produits par extraction_stats.py.

Six figures sont écrites dans `../assets/` :
  1. apercu-kpi.png            : tableau d'indicateurs (image d'en-tête)
  2. distribution-anciennete.png : histogramme et courbe cumulée de l'ancienneté
  3. anciennete-absences.png   : nuage de points, droite de régression, prédictions
  4. rebellion-sexe.png        : actes de rébellion et lien avec le sexe
  5. normalite-salaires.png    : effectifs observés et théoriques des salaires
  6. robustesse-decisions.png  : marge de décision des quatre tests

Palette catégorielle validée pour la vision des couleurs (écarts CVD ΔE >= 8 sur
les paires adjacentes). Chaque série porte en plus une étiquette directe, de
sorte que la couleur n'est jamais le seul repère.

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
        # Sans cette option, une chaîne contenant deux « $ » est interprétée
        # comme une formule mathématique par matplotlib.
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

MOINS = "−"  # signe moins typographique, plus lisible que le trait d'union


def nombre(valeur, decimales=2):
    """12.5809 -> '12,58'"""
    texte = f"{abs(valeur):,.{decimales}f}".replace(",", " ").replace(".", ",")
    return f"{MOINS if valeur < 0 else ''}{texte}"


def dollars(valeur, decimales=0):
    return f"{nombre(valeur, decimales)} $"


def pourcent(valeur, decimales=1):
    return f"{nombre(valeur * 100, decimales)} %"


def depouiller(ax, garder=("left", "bottom")):
    for cote, epine in ax.spines.items():
        epine.set_visible(cote in garder)
        if cote in garder:
            epine.set_linewidth(0.8)
    ax.tick_params(length=0, labelsize=9)


def titrer(fig, titre, sous_titre=None, y=0.975):
    fig.text(0.012, y, titre, fontsize=15, fontweight="bold", color=ENCRE, va="top")
    if sous_titre:
        fig.text(0.012, y - 0.048, sous_titre, fontsize=10, color=ENCRE_2, va="top")


def signer(fig, source="Source : analyse-statistique.xlsx · Issa Ouedraogo"):
    fig.text(0.012, 0.012, source, fontsize=8, color=ENCRE_MUET)


# =========================================================================
# 1. Tableau d'indicateurs
# =========================================================================
def figure_kpi(mesures, profil, regression, croise, ic, tests, portee, sensibilite):
    m = mesures.iloc[0]
    p = profil.iloc[0]
    reg = regression.iloc[0]
    ic_corrige = ic.iloc[1]
    femmes = croise.loc[croise["sexe"] == "Femme"].iloc[0]
    hommes = croise.loc[croise["sexe"] == "Homme"].iloc[0]
    khi2 = tests.iloc[0]
    proportion = tests.iloc[3]
    experimentes = portee.iloc[0]
    bascule = sensibilite.loc[sensibilite["seuil"] == 0.06].iloc[0]

    tuiles = [
        ("Employés analysés", f"{int(p['employes'])}",
         f"sur une population de {int(ic_corrige['N'])} · taux de sondage "
         f"{pourcent(ic_corrige['taux_sondage'])}", "neutre"),
        ("Ancienneté moyenne", f"{nombre(m['moyenne'])} ans",
         f"écart-type {nombre(m['ecart_type'])} · coefficient de variation "
         f"{pourcent(m['coefficient_variation'])}", "neutre"),
        ("Intervalle de confiance 97 %", f"{nombre(ic_corrige['borne_inferieure'])} à "
         f"{nombre(ic_corrige['borne_superieure'])} ans",
         "avec correction de population finie", "bon"),
        ("Corrélation ancienneté et absences", nombre(reg["r"], 3),
         f"la régression explique {pourcent(reg['r_carre'])} des absences", "bon"),
        ("Employés ayant commis un acte", pourcent(p["part_rebelles"]),
         f"{int(p['employes_rebelles'])} employés · {int(p['actes_totaux'])} actes · "
         f"{nombre(p['actes_par_rebelle'])} actes chacun", "mauvais"),
        ("Écart hommes et femmes", f"{pourcent(hommes['taux_rebellion'])} contre "
         f"{pourcent(femmes['taux_rebellion'])}",
         f"khi-deux {nombre(khi2['statistique'])} contre "
         f"{nombre(khi2['valeur_critique'])} critique", "mauvais"),
        ("Salaire moyen des manœuvres expérimentés", dollars(experimentes["salaire_moyen"]),
         f"n = {int(experimentes['n'])} · test contre 44 000 $ : "
         f"p < 0,001", "neutre"),
        ("Pièces non conformes", pourcent(bascule["proportion_observee"], 3),
         f"seuil critique {pourcent(bascule['proportion_critique'], 3)} · "
         f"1 pièce sépare les deux conclusions", "mauvais"),
    ]

    couleurs = {"bon": BON, "mauvais": CRITIQUE, "neutre": BLEU_FONCE}

    fig = plt.figure(figsize=(12.6, 5.0))
    titrer(
        fig,
        "Analyse statistique d'un échantillon de 225 employés : indicateurs clés",
        "Abus inc. · manœuvres beaucerons · pièces Kansas Vamal "
        "· quatre tests d'hypothèses",
    )

    n_col, n_lig = 4, 2
    marge_g, marge_d = 0.012, 0.012
    haut, bas = 0.80, 0.09
    ecart_x, ecart_y = 0.016, 0.055
    larg = (1 - marge_g - marge_d - (n_col - 1) * ecart_x) / n_col
    haut_t = (haut - bas - (n_lig - 1) * ecart_y) / n_lig

    for i, (libelle, valeur, note, ton) in enumerate(tuiles):
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
        fig.patches.append(
            plt.Rectangle(
                (x, y), 0.004, haut_t, transform=fig.transFigure,
                facecolor=couleurs[ton], edgecolor="none", zorder=1,
            )
        )
        fig.text(x + 0.018, y + haut_t - 0.045, libelle, fontsize=9, color=ENCRE_2)
        fig.text(
            x + 0.018, y + haut_t - 0.135, valeur,
            fontsize=17, fontweight="bold", color=couleurs[ton], va="top",
        )
        fig.text(x + 0.018, y + 0.022, note, fontsize=8, color=ENCRE_MUET)

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "apercu-kpi.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 2. Distribution de l'ancienneté
# =========================================================================
def figure_anciennete(distribution, mesures):
    m = mesures.iloc[0]
    milieux = (distribution["borne_inf"] + distribution["borne_sup"]) / 2

    fig, ax = plt.subplots(figsize=(12.6, 5.4))
    fig.subplots_adjust(left=0.06, right=0.93, top=0.76, bottom=0.14)
    titrer(
        fig,
        "Une main-d'œuvre homogène et concentrée autour de 12 ans d'ancienneté",
        "Répartition des 225 employés d'Abus inc. par classe de 3 années "
        "· effectifs du classeur reproduits à l'identique",
    )

    ax.bar(
        milieux, distribution["effectif"], width=2.75,
        color=BLEU_PALE, edgecolor=BLEU, linewidth=1.2, zorder=3,
    )
    for x, effectif, frequence in zip(
        milieux, distribution["effectif"], distribution["frequence"]
    ):
        ax.text(
            x, effectif + 2.4, f"{effectif}\n{pourcent(frequence, 1)}",
            ha="center", va="bottom", fontsize=8.5, color=ENCRE_2, linespacing=1.4,
        )

    # Moyenne et médiane se superposent à 4 centièmes d'année près : une seule
    # ligne suffit, et cette coïncidence est en elle-même le résultat à montrer.
    ax.axvline(m["moyenne"], color=ORANGE, linewidth=1.8, zorder=4)
    ax.annotate(
        f"moyenne {nombre(m['moyenne'])} ans\nmédiane {nombre(m['mediane'])} ans\n"
        f"la distribution est symétrique",
        xy=(m["moyenne"], 62), xytext=(9.9, 92),
        color=ORANGE, fontsize=9, fontweight="bold", ha="right", va="top",
        linespacing=1.5,
        arrowprops=dict(arrowstyle="-", color=ORANGE, linewidth=1.1),
    )

    ax.set_ylim(0, 96)
    ax.set_xlabel("Ancienneté (années)")
    ax.set_ylabel("Nombre d'employés")
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.grid(axis="y", zorder=0)
    depouiller(ax)

    ax2 = ax.twinx()
    ax2.plot(
        distribution["borne_sup"], distribution["frequence_cumulee"],
        color=BLEU_FONCE, linewidth=1.6, marker="o", markersize=4, zorder=5,
    )
    ax2.set_ylim(0, 1.09)
    ax2.set_ylabel("Fréquence cumulée", color=BLEU_FONCE)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax2.set_yticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"], color=BLEU_FONCE)
    depouiller(ax2, garder=("bottom",))
    ax2.text(
        21.4, 0.58,
        f"{pourcent(distribution['frequence_cumulee'].iloc[3], 0)} des employés ont moins de "
        f"{nombre(distribution['borne_sup'].iloc[3], 1)} années\nd'ancienneté, "
        f"{pourcent(1 - distribution['frequence_cumulee'].iloc[5], 0)} en ont plus de "
        f"{nombre(distribution['borne_sup'].iloc[5], 1)}",
        fontsize=8.5, color=BLEU_FONCE, va="top", linespacing=1.5, ha="center",
    )

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "distribution-anciennete.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 3. Ancienneté et absences : régression et prédictions
# =========================================================================
def figure_regression(echantillon, regression, qualite):
    reg = regression.iloc[0]
    sans_zero = qualite.iloc[1]
    zeros = qualite.iloc[2]

    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    fig.subplots_adjust(left=0.06, right=0.99, top=0.75, bottom=0.15)
    titrer(
        fig,
        "Plus un employé est ancien, moins il s'absente",
        f"225 employés · r = {nombre(reg['r'], 3)} · la régression explique "
        f"{pourcent(reg['r_carre'])} de la variation des absences",
    )

    presents = echantillon[echantillon["jours_absence"] > 0]
    absents = echantillon[echantillon["jours_absence"] == 0]
    ax.scatter(
        presents["anciennete"], presents["jours_absence"],
        s=26, color=BLEU, alpha=0.42, edgecolor="none", zorder=3,
    )
    ax.scatter(
        absents["anciennete"], absents["jours_absence"],
        s=44, color=JAUNE, marker="D", edgecolor=SURFACE, linewidth=1.0, zorder=6,
    )
    ax.annotate(
        f"{int(zeros['n'])} employés déclarés à zéro jour, répartis sur toute la plage\n"
        f"d'ancienneté : leurs résidus vont de {nombre(zeros['residu_min'])} à "
        f"{nombre(zeros['residu_max'])} jours, hors de la bande des autres.\n"
        f"En les écartant, r passe à {nombre(sans_zero['r'], 3)} et le pouvoir explicatif "
        f"à {pourcent(sans_zero['r_carre'])}.",
        xy=(9.2, 0), xytext=(2.2, 14),
        fontsize=8.5, color="#8a5f00", linespacing=1.55,
        arrowprops=dict(arrowstyle="-", color=JAUNE, linewidth=1.2),
    )

    x_min, x_max = reg["anciennete_min"], reg["anciennete_max"]
    xs = [x_min, x_max]
    ys = [reg["ordonnee_origine"] + reg["pente"] * x for x in xs]
    ax.plot(xs, ys, color=ORANGE, linewidth=2.4, zorder=5)
    ax.text(
        x_max - 0.4, ys[1] - 3.4,
        f"y = {nombre(reg['ordonnee_origine'])} {MOINS} "
        f"{nombre(abs(reg['pente']))} x",
        color=ORANGE, fontsize=9.5, fontweight="bold", ha="right",
    )

    # Prédiction demandée à 20,55 années : la valeur du classeur repose sur la
    # pente inverse (régression de l'ancienneté sur les absences).
    x_pred = 20.55
    y_correct = reg["prediction_20_55"]
    y_pente_inverse = reg["prediction_20_55_pente_inverse"]
    ax.scatter([x_pred], [y_correct], s=110, color=BON, zorder=7,
               edgecolor=SURFACE, linewidth=1.6)
    ax.annotate(
        f"prédiction recalculée\n{nombre(y_correct)} jours",
        xy=(x_pred, y_correct), xytext=(19.6, 26.5),
        fontsize=9, color=BON, fontweight="bold", linespacing=1.4,
        arrowprops=dict(arrowstyle="-", color=BON, linewidth=1.2),
    )
    ax.scatter([x_pred], [y_pente_inverse], s=110, color=CRITIQUE, marker="X", zorder=7,
               edgecolor=SURFACE, linewidth=1.2)
    ax.annotate(
        f"avec la pente inverse ({nombre(reg['pente_inverse_x_sur_y'], 3)})\n"
        f"{nombre(y_pente_inverse)} jours : à ne pas confondre",
        xy=(x_pred, y_pente_inverse), xytext=(15.4, 34.5),
        fontsize=9, color=CRITIQUE, fontweight="bold", linespacing=1.4,
        arrowprops=dict(arrowstyle="-", color=CRITIQUE, linewidth=1.2),
    )

    ax.axvspan(x_max, 27, color=GRILLE, alpha=0.55, zorder=1)
    ax.text(
        x_max + 0.4, 52,
        "au-delà de 24,1 années,\naucune donnée : la droite\nprédirait des absences\nnégatives dès 25 ans",
        fontsize=8.5, color=ENCRE_2, va="top", linespacing=1.5,
    )

    ax.set_xlim(0, 27)
    ax.set_ylim(-2, 58)
    ax.set_xlabel("Ancienneté (années)")
    ax.set_ylabel("Jours d'absence de courte durée")
    ax.grid(axis="y", zorder=0)
    depouiller(ax)

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "anciennete-absences.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 4. Rébellion : nature des actes et lien avec le sexe
# =========================================================================
def figure_rebellion(actes, croise, tests, profil):
    khi2 = tests.iloc[0]
    p = profil.iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.4), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(left=0.185, right=0.985, top=0.74, bottom=0.18, wspace=0.42)
    titrer(
        fig,
        "146 actes de rébellion, concentrés sur un quart des employés",
        f"{int(p['employes_rebelles'])} employés sur {int(p['employes'])} ont commis au moins un acte "
        f"· {nombre(p['actes_par_rebelle'])} actes en moyenne par employé concerné",
    )

    # --- Nature des actes
    ordre = actes.sort_values("nombre_actes")
    positions = range(len(ordre))
    couleurs = [
        ORANGE if libelle.startswith(("1", "2")) else BLEU_PALE
        for libelle in ordre["acte"]
    ]
    ax1.barh(positions, ordre["nombre_actes"], height=0.62, color=couleurs,
             edgecolor="none", zorder=3)
    for y, (nb, part) in enumerate(zip(ordre["nombre_actes"], ordre["part_des_actes"])):
        ax1.text(nb + 1.6, y, f"{nb}  ({pourcent(part)})", va="center",
                 fontsize=9, color=ENCRE_2)
    ax1.set_yticks(list(positions))
    ax1.set_yticklabels(ordre["acte"], fontsize=9)
    ax1.set_xlim(0, 95)
    ax1.set_xlabel("Nombre d'actes recensés")
    ax1.set_title(
        "Les deux formes les moins graves font 76 % du total",
        fontsize=10.5, color=ENCRE, loc="left", pad=12,
    )
    ax1.grid(axis="x", zorder=0)
    depouiller(ax1)

    # --- Taux de rébellion par sexe
    sexes = list(croise["sexe"])
    taux = list(croise["taux_rebellion"])
    barres = ax2.bar(sexes, taux, width=0.46, color=[AQUA, ORANGE],
                     edgecolor="none", zorder=3)
    for barre, valeur, ligne in zip(barres, taux, croise.itertuples()):
        ax2.text(
            barre.get_x() + barre.get_width() / 2, valeur + 0.012,
            f"{pourcent(valeur)}\n{ligne.au_moins_un_acte} sur {ligne.total}",
            ha="center", fontsize=9.5, color=ENCRE_2, linespacing=1.4,
        )
    ax2.set_ylim(0, 0.40)
    ax2.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
    ax2.set_yticklabels(["0 %", "10 %", "20 %", "30 %", "40 %"])
    ax2.set_ylabel("Part des employés ayant commis un acte")
    ax2.set_title(
        "Un homme est deux fois plus susceptible d'en commettre un",
        fontsize=10.5, color=ENCRE, loc="left", pad=12,
    )
    ax2.grid(axis="y", zorder=0)
    depouiller(ax2)

    fig.text(
        0.185, 0.055,
        f"Khi-deux {nombre(khi2['statistique'])} contre "
        f"{nombre(khi2['valeur_critique'])} critique (p = {nombre(khi2['p_valeur'], 3)}) : "
        f"le lien est confirmé, et le resterait au seuil de 5 %. Le tableau croise "
        f"des employés et non des actes : les {int(p['actes_totaux'])} actes sont "
        f"le fait de {int(p['employes_rebelles'])} personnes.",
        fontsize=8.5, color=ENCRE_2,
    )

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "rebellion-sexe.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 5. Normalité des salaires beaucerons
# =========================================================================
def figure_normalite(salaires, tests, parametres):
    test = tests.iloc[1]
    par = parametres.iloc[0]
    positions = range(len(salaires))
    largeur = 0.38

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.6, 5.4), gridspec_kw={"width_ratios": [1.6, 1]}
    )
    fig.subplots_adjust(left=0.055, right=0.985, top=0.74, bottom=0.20, wspace=0.28)
    titrer(
        fig,
        "L'assertion du regroupement patronal résiste au test",
        f"150 manœuvres beaucerons · khi-deux d'ajustement "
        f"{nombre(test['statistique'])} contre {nombre(test['valeur_critique'])} critique "
        f"· H0 non rejetée au seuil de 5 %",
    )

    ax1.bar([p - largeur / 2 for p in positions], salaires["effectif_observe"],
            width=largeur, color=BLEU, edgecolor="none", zorder=3, label="Observé")
    ax1.bar([p + largeur / 2 for p in positions], salaires["effectif_theorique"],
            width=largeur, color=JAUNE, edgecolor="none", zorder=3,
            label="Théorique · loi normale (36 300 $ ; 9 500 $)")
    for x, (obs, theo) in enumerate(
        zip(salaires["effectif_observe"], salaires["effectif_theorique"])
    ):
        ax1.text(x - largeur / 2, obs + 0.9, f"{int(obs)}", ha="center",
                 fontsize=8.5, color=BLEU_FONCE)
        ax1.text(x + largeur / 2, theo + 0.9, nombre(theo, 1), ha="center",
                 fontsize=8.5, color="#8a5f00")
    ax1.set_xticks(list(positions))
    ax1.set_xticklabels(
        [c.replace(" à ", "\nà\n").replace(" $", "") for c in salaires["classe"]],
        fontsize=8.5, linespacing=1.3,
    )
    ax1.set_ylabel("Nombre de manœuvres")
    ax1.set_ylim(0, 56)
    ax1.grid(axis="y", zorder=0)
    ax1.legend(frameon=False, fontsize=8.5, loc="upper left", ncols=1)
    depouiller(ax1)

    # Contributions au khi-deux
    ordre = salaires.sort_values("contribution_khi2")
    ax2.barh(range(len(ordre)), ordre["contribution_khi2"], height=0.6,
             color=[CRITIQUE if v > 2 else BLEU_PALE for v in ordre["contribution_khi2"]],
             edgecolor="none", zorder=3)
    for y, v in enumerate(ordre["contribution_khi2"]):
        ax2.text(v + 0.06, y, nombre(v), va="center", fontsize=8.5, color=ENCRE_2)
    ax2.set_yticks(range(len(ordre)))
    ax2.set_yticklabels(
        [c.replace(" $", "") for c in ordre["classe"]], fontsize=8.5
    )
    ax2.set_xlim(0, 4.4)
    ax2.set_xlabel("Contribution au khi-deux")
    ax2.set_title(
        "Deux classes portent 60 % de l'écart",
        fontsize=10.5, color=ENCRE, loc="left", pad=12,
    )
    ax2.grid(axis="x", zorder=0)
    depouiller(ax2)

    fig.text(
        0.055, 0.055,
        f"Moyenne observée {dollars(par['moyenne_observee'])} contre "
        f"{dollars(par['moyenne_theorique'])} postulés  ·  écart-type observé "
        f"{dollars(par['ecart_type_observe'])} contre {dollars(par['ecart_type_theorique'])}  ·  "
        f"troisième quartile du modèle {dollars(par['q3_theorique'], 2)}",
        fontsize=8.5, color=ENCRE_2,
    )

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "normalite-salaires.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
# 6. Robustesse des quatre décisions
# =========================================================================
def figure_robustesse(tests, sensibilite, ic):
    libelles = [
        "Lien entre le sexe\net la rébellion",
        "Normalité des salaires\nbeaucerons",
        "Salaire moyen\ninférieur à 44 000 $",
        "Hausse des pièces\nnon conformes",
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.6, 5.6), gridspec_kw={"width_ratios": [1.5, 1]}
    )
    fig.subplots_adjust(left=0.14, right=0.985, top=0.74, bottom=0.15, wspace=0.30)
    titrer(
        fig,
        "Trois décisions solides, une décision qui tient à une seule pièce",
        "Seuil observé de chaque test comparé à son seuil de signification "
        "· échelle logarithmique",
    )

    positions = list(range(len(tests)))[::-1]
    for y, (_, ligne), libelle in zip(positions, tests.iterrows(), libelles):
        p_valeur = ligne["p_valeur"]
        seuil = ligne["seuil"]
        rejet = ligne["decision"] == "rejet de H0"
        couleur = CRITIQUE if rejet else BLEU_FONCE

        ax1.plot([min(p_valeur, seuil), max(p_valeur, seuil)], [y, y],
                 color=GRILLE, linewidth=6, solid_capstyle="round", zorder=2)
        ax1.scatter([seuil], [y], s=90, marker="|", color=ENCRE_2, zorder=4, linewidth=2)
        ax1.scatter([p_valeur], [y], s=110, color=couleur, zorder=5,
                    edgecolor=SURFACE, linewidth=1.4)
        ax1.text(
            p_valeur * (0.72 if p_valeur < seuil else 1.35), y + 0.22,
            "p < 0,001" if p_valeur < 0.001 else f"p = {nombre(p_valeur, 3)}",
            fontsize=8.5, color=couleur, fontweight="bold",
            ha="right" if p_valeur < seuil else "left",
        )
        ax1.text(
            seuil * 1.25, y - 0.30, f"seuil {pourcent(seuil, 0)}",
            fontsize=8, color=ENCRE_MUET,
        )

    ax1.set_xscale("log")
    ax1.set_xlim(3e-8, 1.6)
    ax1.set_yticks(positions)
    ax1.set_yticklabels(libelles, fontsize=9, linespacing=1.4)
    ax1.set_ylim(-0.7, 3.9)
    ax1.set_xlabel("Seuil observé (p)")
    # Le formateur logarithmique de matplotlib produit des étiquettes en
    # notation mathématique, que « text.parse_math: False » laisse à l'état brut.
    ax1.set_xticks([1e-7, 1e-5, 1e-3, 1e-2, 1e-1, 1])
    ax1.set_xticklabels(
        ["0,00001 %", "0,001 %", "0,1 %", "1 %", "10 %", "100 %"], fontsize=8.5
    )
    ax1.set_xticks([], minor=True)
    ax1.grid(axis="x", zorder=0)
    depouiller(ax1)
    ax1.text(
        3e-8, 3.80,
        "À gauche du trait : H0 rejetée.   À droite du trait : H0 conservée.",
        fontsize=8.5, color=ENCRE_2, va="top",
    )

    # --- Sensibilité du test sur la proportion
    ax2.set_title(
        "Combien de pièces non conformes\nfaudrait-il pour rejeter H0 ?",
        fontsize=10.5, color=ENCRE, loc="left", pad=12,
    )
    seuils = sensibilite["seuil"]
    positions2 = range(len(sensibilite))
    couleurs = [
        CRITIQUE if d == "rejet de H0" else BLEU_PALE for d in sensibilite["decision"]
    ]
    ax2.barh(positions2, sensibilite["pieces_necessaires"], height=0.58,
             color=couleurs, edgecolor="none", zorder=3)
    for y, ligne in enumerate(sensibilite.itertuples()):
        ax2.text(ligne.pieces_necessaires + 0.25, y, f"{ligne.pieces_necessaires}",
                 va="center", fontsize=9, color=ENCRE_2, fontweight="bold")
    ax2.axvline(17, color=ENCRE, linewidth=1.6, linestyle=(0, (4, 2)), zorder=6)
    ax2.text(17.15, -0.62, "17 pièces observées",
             fontsize=8.5, color=ENCRE, fontweight="bold")
    ax2.set_ylim(-0.9, len(sensibilite) - 0.4)
    ax2.set_yticks(list(positions2))
    ax2.set_yticklabels([f"seuil {pourcent(s, 0)}" for s in seuils], fontsize=9)
    ax2.set_xlim(15, 21.4)
    ax2.set_xlabel("Pièces non conformes nécessaires")
    ax2.grid(axis="x", zorder=0)
    depouiller(ax2)

    ic_sans, ic_avec = ic.iloc[0], ic.iloc[1]
    fig.text(
        0.14, 0.045,
        f"Intervalle de confiance à 97 % de l'ancienneté moyenne : "
        f"{nombre(ic_sans['borne_inferieure'])} à {nombre(ic_sans['borne_superieure'])} ans "
        f"sans correction de population finie, "
        f"{nombre(ic_avec['borne_inferieure'])} à {nombre(ic_avec['borne_superieure'])} ans avec "
        f"(taux de sondage {pourcent(ic_avec['taux_sondage'])}).",
        fontsize=8.5, color=ENCRE_2,
    )

    signer(fig)
    fig.savefig(DOSSIER_ASSETS / "robustesse-decisions.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# =========================================================================
def main():
    DOSSIER_ASSETS.mkdir(exist_ok=True)

    def lire(nom):
        return pd.read_csv(DOSSIER_DONNEES / nom)

    echantillon = lire("echantillon_abus.csv")
    distribution = lire("distribution_anciennete.csv")
    mesures = lire("mesures_anciennete.csv")
    actes = lire("actes_rebellion.csv")
    profil = lire("profil_rebellion.csv")
    regression = lire("regression_absences.csv")
    qualite = lire("qualite_absences.csv")
    croise = lire("tableau_croise_sexe.csv")
    ic = lire("intervalle_confiance.csv")
    salaires = lire("distribution_salaires.csv")
    parametres = lire("parametres_salaires.csv")
    portee = lire("portee_test_moyenne.csv")
    tests = lire("tests_hypotheses.csv")
    sensibilite = lire("sensibilite_proportion.csv")

    figure_kpi(mesures, profil, regression, croise, ic, tests, portee, sensibilite)
    figure_anciennete(distribution, mesures)
    figure_regression(echantillon, regression, qualite)
    figure_rebellion(actes, croise, tests, profil)
    figure_normalite(salaires, tests, parametres)
    figure_robustesse(tests, sensibilite, ic)

    print("Six figures écrites dans", DOSSIER_ASSETS)


if __name__ == "__main__":
    main()
