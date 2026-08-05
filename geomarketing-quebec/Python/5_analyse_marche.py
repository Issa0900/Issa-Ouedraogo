"""
Analyses 1 à 5 du projet geomarketing (taille de marché, croissance, concurrence, profil
client, score d'opportunité). Lit les CSV réels dans data/, écrit data/synthese_regions.csv
(source pour Power BI) et un graphique du score d'opportunité.

Sources et méthodologie : voir data/SOURCES.md.
- isq_regions.csv : population, croissance, revenu disponible et taux de chômage extraits
  des fiches "Coup d'œil sur les régions" de l'ISQ (chaque indicateur a sa propre année de
  référence, indiquée dans les colonnes annee_*).
- entreprises_regions.csv : nombre d'établissements par région, agrégé depuis le registre
  des entreprises du Québec (Registraire des entreprises) en rattachant la ville de chaque
  établissement à sa région administrative. ~81% des établissements ont pu être rattachés à
  une région (le reste porte des noms de ville hors du dictionnaire de correspondance utilisé
  et n'est pas compté) — l'indice de concurrence est donc une estimation par défaut.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PONDERATION = {
    "population": 0.40,
    "revenu": 0.30,
    "croissance": 0.20,
    "faible_concurrence": 0.10,
}


def normaliser(colonne: pd.Series) -> pd.Series:
    return (colonne - colonne.min()) / (colonne.max() - colonne.min())


def charger_donnees() -> pd.DataFrame:
    isq = pd.read_csv(DATA_DIR / "isq_regions.csv")
    entreprises = pd.read_csv(DATA_DIR / "entreprises_regions.csv")
    df = isq.merge(entreprises, on="nom_region", how="left")
    df["nb_entreprises"] = df["nb_entreprises"].fillna(0)
    return df


def calculer_analyses(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Analyse 1 — taille du marché
    df["potentiel_marche"] = df["population_totale"] * df["revenu_disponible_habitant"]

    # Analyse 2 — croissance démographique (déjà fournie par la source ISQ, en %)
    df["croissance_pct"] = df["croissance_pct_annuelle"]

    # Analyse 3 — intensité concurrentielle
    df["indice_concurrence"] = df["nb_entreprises"] / df["population_totale"]

    # Analyse 5 — score d'opportunité
    df["score_population"] = normaliser(df["population_totale"])
    df["score_revenu"] = normaliser(df["revenu_disponible_habitant"])
    df["score_croissance"] = normaliser(df["croissance_pct"])
    df["score_faible_concurrence"] = 1 - normaliser(df["indice_concurrence"])

    df["score_opportunite"] = 100 * (
        PONDERATION["population"] * df["score_population"]
        + PONDERATION["revenu"] * df["score_revenu"]
        + PONDERATION["croissance"] * df["score_croissance"]
        + PONDERATION["faible_concurrence"] * df["score_faible_concurrence"]
    )

    return df.sort_values("score_opportunite", ascending=False)


def construire_historique(classement: pd.DataFrame) -> pd.DataFrame:
    enregistrements = []

    for _, row in classement.iterrows():
        population_estimee = float(row["population_totale"])
        croissance = float(row.get("croissance_pct_annuelle", 0.0)) / 100.0

        for annee in [2023, 2022, 2021, 2020]:
            enregistrements.append(
                {
                    "nom_region": row["nom_region"],
                    "annee": annee,
                    "population_estimee": population_estimee,
                    "croissance_pct_annuelle": row.get("croissance_pct_annuelle", 0.0),
                }
            )
            if annee > 2020:
                population_estimee = population_estimee / (1 + croissance) if croissance != 0 else population_estimee

    historique = pd.DataFrame(enregistrements)
    return historique.sort_values(["nom_region", "annee"]).reset_index(drop=True)


def exporter(classement: pd.DataFrame) -> None:
    colonnes = [
        "nom_region", "population_totale", "annee_population", "croissance_pct_annuelle",
        "revenu_disponible_habitant", "annee_revenu", "taux_chomage", "annee_chomage",
        "nb_entreprises", "potentiel_marche", "indice_concurrence", "score_opportunite",
    ]
    classement[colonnes].to_csv(DATA_DIR / "synthese_regions.csv", index=False, encoding="utf-8-sig")

    historique = construire_historique(classement)
    historique[["nom_region", "annee", "population_estimee", "croissance_pct_annuelle"]].to_csv(
        DATA_DIR / "synthese_regions_historique.csv",
        index=False,
        encoding="utf-8-sig",
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(classement["nom_region"], classement["score_opportunite"], color="#2b6cb0")
    ax.set_xlabel("Score d'opportunité (/100)")
    ax.set_title("Score d'opportunité commerciale par région — Québec")
    ax.invert_yaxis()
    fig.tight_layout()
    out_png = DATA_DIR.parent / "Rapport" / "score_opportunite.png"
    fig.savefig(out_png, dpi=150)
    print(f"Graphique : {out_png}")


if __name__ == "__main__":
    donnees = charger_donnees()
    classement = calculer_analyses(donnees)
    exporter(classement)
    print(classement[["nom_region", "score_opportunite", "population_totale",
                       "revenu_disponible_habitant", "indice_concurrence"]].to_string(index=False))
