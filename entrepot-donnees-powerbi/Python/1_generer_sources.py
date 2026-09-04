"""
1_generer_sources.py — Genere les 8 fichiers sources bruts de Boreal Distribution inc.

Simule ce qu'une PME exporte reellement de ses systemes : un ERP, un CRM, un
classeur RH, des extractions comptables. Chaque fichier a son propre format,
son propre encodage et ses propres defauts.

Les anomalies ne sont PAS accidentelles : elles sont injectees volontairement et
comptabilisees, pour que l'ETL (script 2) ait quelque chose de reel a nettoyer et
que le rapport qualite (script 3) puisse etre verifie ligne a ligne.

Seed fixe (RANDOM_SEED) => le jeu de donnees est identique a chaque execution.
Les chiffres cites dans le README proviennent donc de ce jeu precis.
"""

from __future__ import annotations

import csv
import json
import os
import random
import re
import unicodedata
from datetime import date, datetime, timedelta

RANDOM_SEED = 20260904
rng = random.Random(RANDOM_SEED)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUT = os.path.join(BASE, "data", "brut")
os.makedirs(BRUT, exist_ok=True)

DEBUT = date(2024, 1, 1)
FIN = date(2025, 12, 31)

# Compteur d'anomalies injectees, ecrit en fin de script dans data/brut/_anomalies_injectees.json.
# C'est la reference contre laquelle le rapport qualite du script 3 est confronte.
INJECTE: dict[str, int] = {}


def compter(cle: str, n: int = 1) -> None:
    INJECTE[cle] = INJECTE.get(cle, 0) + n


def sans_accent(txt: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# Referentiels : l'entreprise fictive
# ---------------------------------------------------------------------------

ENTREPOTS = [
    {"code": "ENT-QC", "nom": "Quebec", "region": "Capitale-Nationale", "surface_m2": 2800},
    {"code": "ENT-MTL", "nom": "Montreal", "region": "Montreal", "surface_m2": 4200},
    {"code": "ENT-SAG", "nom": "Saguenay", "region": "Saguenay-Lac-Saint-Jean", "surface_m2": 1900},
]

# saison = mois ou la famille se vend le mieux (multiplicateur de demande)
FAMILLES = {
    "Camping":              {"saison": [5, 6, 7, 8],       "marge_cible": 0.42},
    "Randonnee":            {"saison": [4, 5, 6, 7, 8, 9], "marge_cible": 0.40},
    "Vetements techniques": {"saison": [9, 10, 11, 12],    "marge_cible": 0.45},
    "Peche":                {"saison": [5, 6, 7],          "marge_cible": 0.38},
    "Sports d'hiver":       {"saison": [10, 11, 12, 1],    "marge_cible": 0.41},
    "Accessoires":          {"saison": [],                 "marge_cible": 0.48},
}

NOMS_FOURNISSEURS = [
    ("Nordik Textile inc.", "Canada"), ("Alpin Équipement ltée", "Canada"),
    ("Great Lakes Outdoor Co.", "États-Unis"), ("Sentier Nord", "Canada"),
    ("Vertex Gear Supply", "États-Unis"), ("Fibrelac Manufacturing", "Canada"),
    ("Han Yang Textiles", "Vietnam"), ("Summit Trading Ltd", "Chine"),
    ("Boréale Plein Air", "Canada"), ("Cascade Sports Import", "États-Unis"),
    ("Laurentide Outillage", "Canada"), ("PolarTech Fabrics", "Canada"),
    ("Rivière Bleue Pêche", "Canada"), ("Delta Angling Supply", "États-Unis"),
    ("Mont-Blanc Distribution", "Canada"), ("Kestrel Import Group", "Chine"),
    ("Forêt Verte Accessoires", "Canada"), ("Tundra Winter Goods", "Canada"),
    ("Saguenay Metal Works", "Canada"), ("Pacific Rim Textiles", "Vietnam"),
    ("Chemin Faisant inc.", "Canada"), ("Northwind Apparel", "États-Unis"),
]

# Le fournisseur dont le cout derive : c'est l'histoire centrale du tableau de bord.
FOURNISSEUR_DERIVE = "Nordik Textile inc."
DEBUT_DERIVE = date(2025, 5, 1)
AMPLEUR_DERIVE = 1.18  # +18 % sur le cout d'achat unitaire

fournisseurs = []
for i, (nom, pays) in enumerate(NOMS_FOURNISSEURS, start=1):
    fournisseurs.append({
        "code": f"FRN-{i:03d}",
        "nom": nom,
        "pays": pays,
        "delai_moyen_jours": rng.choice([7, 10, 14, 21, 28, 35, 45]),
        "conditions": rng.choice(["Net 30", "Net 45", "Net 60", "2/10 Net 30"]),
    })

MOTS_PRODUIT = {
    "Camping": ["Tente", "Sac de couchage", "Matelas gonflable", "Rechaud", "Lanterne",
                "Glaciere", "Chaise pliante", "Bache", "Popote", "Hamac"],
    "Randonnee": ["Sac a dos", "Batons", "Bottes", "Gourde", "Trousse premiers soins",
                  "Boussole", "Guetres", "Lampe frontale"],
    "Vetements techniques": ["Manteau isole", "Coquille impermeable", "Pantalon coque",
                             "Chandail polaire", "Sous-vetement merinos", "Tuque technique",
                             "Gants isoles", "Cagoule"],
    "Peche": ["Canne a peche", "Moulinet", "Coffre a leurres", "Waders", "Epuisette",
              "Ligne tressee", "Boite de mouches"],
    "Sports d'hiver": ["Raquettes", "Skis de fond", "Fixations", "Casque", "Lunettes de ski",
                       "Traineau", "Crampons", "Peaux d'ascension"],
    "Accessoires": ["Couteau multifonction", "Sifflet de securite", "Corde", "Mousqueton",
                    "Sangle", "Trousse de reparation", "Sac etanche", "Filtre a eau"],
}
QUALIFICATIFS = ["Alpin", "Boreal", "Nordet", "Sommet", "Traverse", "Expedition", "Sentier",
                 "Cap-Nord", "Taiga", "Portage", "Escarpement", "Grand-Nord"]

produits = []
sku_num = 1000
for famille, cfg in FAMILLES.items():
    frn_famille = rng.sample(fournisseurs, k=rng.randint(3, 5))
    n_produits = {"Camping": 34, "Randonnee": 30, "Vetements techniques": 38,
                  "Peche": 24, "Sports d'hiver": 30, "Accessoires": 26}[famille]
    for _ in range(n_produits):
        sku_num += 1
        base = rng.choice(MOTS_PRODUIT[famille])
        nom = f"{base} {rng.choice(QUALIFICATIFS)} {rng.choice(['100', '200', '300', 'Pro', 'XT', 'Lite'])}"
        cout = round(rng.uniform(12, 340), 2)
        marge = cfg["marge_cible"] + rng.uniform(-0.06, 0.06)
        prix = round(cout / (1 - marge), 2)
        produits.append({
            "sku": f"BD-{sku_num}",
            "nom": nom,
            "famille": famille,
            "fournisseur": rng.choice(frn_famille)["code"],
            "cout_standard": cout,
            "prix_liste": prix,
            "poids_kg": round(rng.uniform(0.1, 14.0), 2),
        })

VILLES_QC = ["Quebec", "Montreal", "Laval", "Gatineau", "Sherbrooke", "Trois-Rivieres",
             "Saguenay", "Levis", "Terrebonne", "Saint-Jean-sur-Richelieu", "Rimouski",
             "Drummondville", "Granby", "Saint-Jerome", "Val-d'Or", "Rouyn-Noranda",
             "Baie-Comeau", "Sept-Iles", "Victoriaville", "Shawinigan"]
VILLES_ON = ["Ottawa", "Toronto", "Sudbury", "Thunder Bay", "Kingston", "North Bay"]
VILLES_MARITIMES = ["Moncton", "Fredericton", "Halifax", "Charlottetown", "Bathurst"]

TYPES_CLIENT = ["Detaillant independant", "Chaine regionale", "Boutique en ligne",
                "Cooperative de plein air"]
PREFIXES_CLIENT = ["Plein Air", "Boutique", "Sports", "Aventure", "Le Refuge", "Coopérative",
                   "Chalet", "Grand Air", "Expédition", "Nature", "Base Camp", "Randonneurs",
                   "Le Portage", "Cap Nord", "Sentiers"]
SUFFIXES_CLIENT = ["du Nord", "Laurentides", "Saint-Laurent", "Outaouais", "Charlevoix",
                   "Appalaches", "Gaspésie", "Abitibi", "Cantons", "Mauricie", "inc.",
                   "ltée", "et Fils", "Enr.", "Boréal"]

QUARTIERS = ["Beauport", "Sillery", "Rosemont", "Verdun", "Hull", "Lennoxville",
             "Jonquière", "Chicoutimi", "Sainte-Foy", "Anjou", "Lachine", "Longueuil",
             "Brossard", "Repentigny", "Boucherville", "Blainville", "Mirabel",
             "Saint-Hubert", "Pointe-Claire", "Vaudreuil"]

noms_pris: set[str] = set()
clients = []
for i in range(1, 221):
    ville = rng.choices([rng.choice(VILLES_QC), rng.choice(VILLES_ON), rng.choice(VILLES_MARITIMES)],
                        weights=[0.76, 0.15, 0.09])[0]
    if ville in VILLES_ON:
        province = "ON"
    elif ville in VILLES_MARITIMES:
        province = {"Moncton": "NB", "Fredericton": "NB", "Bathurst": "NB",
                    "Halifax": "NS", "Charlottetown": "PE"}[ville]
    else:
        province = "QC"
    # Segment A = gros comptes (la concentration client est un insight du tableau de bord)
    segment = rng.choices(["A", "B", "C"], weights=[0.055, 0.30, 0.645])[0]
    # Les raisons sociales doivent rester uniques : le rapprochement des doublons
    # clients (script 2) s'appuie sur le nom, deux vrais clients homonymes seraient
    # fusionnes a tort et fausseraient la mesure de qualite.
    nom = f"{rng.choice(PREFIXES_CLIENT)} {rng.choice(SUFFIXES_CLIENT)}"
    while nom in noms_pris:
        nom = (f"{rng.choice(PREFIXES_CLIENT)} {rng.choice(QUARTIERS)} "
               f"{rng.choice(SUFFIXES_CLIENT)}")
    noms_pris.add(nom)
    clients.append({
        "code": f"CLI-{i:04d}",
        "nom": nom,
        "type": rng.choice(TYPES_CLIENT),
        "ville": ville,
        "province": province,
        "code_postal": f"{rng.choice('GHJKLMNR')}{rng.randint(0,9)}{rng.choice('ABCEGHJKLMNPRSTVXY')} "
                       f"{rng.randint(0,9)}{rng.choice('ABCEGHJKLMNPRSTVXY')}{rng.randint(0,9)}",
        "segment": segment,
        "conditions_paiement": rng.choice(["Net 30", "Net 30", "Net 45", "Net 60"]),
        "date_ouverture": DEBUT - timedelta(days=rng.randint(30, 2900)),
        "courriel": f"achats@{sans_accent(nom).lower().replace(' ', '').replace('.', '').replace(chr(39), '')}.ca",
    })

PRENOMS = ["Marie", "Julien", "Sophie", "Alexandre", "Isabelle", "Mathieu", "Geneviève",
           "Patrick", "Caroline", "Sébastien", "Nathalie", "Vincent", "Mélanie", "François",
           "Josée", "Simon", "Karine", "Olivier", "Chantal", "Guillaume", "Amélie", "Martin",
           "Véronique", "Nicolas", "Stéphanie", "Éric", "Catherine", "Jean-Philippe", "Sylvie",
           "Maxime", "Annie", "Charles", "Émilie", "Daniel", "Pascale", "Luc", "Sandra",
           "Antoine", "Manon", "David", "Julie", "Étienne"]
NOMS_FAM = ["Tremblay", "Gagnon", "Roy", "Côté", "Bouchard", "Gauthier", "Morin", "Lavoie",
            "Fortin", "Gagné", "Ouellet", "Pelletier", "Bélanger", "Lévesque", "Bergeron",
            "Leblanc", "Paquette", "Girard", "Simard", "Boucher", "Caron", "Beaulieu",
            "Cloutier", "Dubé", "Poirier", "Fournier", "Lapointe", "Leclerc", "Lefebvre",
            "Poulin", "Thibault", "Nadeau", "Martel", "Bérubé", "Desjardins", "Hébert",
            "Grenier", "Bédard", "Rousseau", "Dufour", "Turcotte", "Lachance"]

POSTES = [
    ("Representant des ventes", "Ventes", 52000, 68000, 9),
    ("Directeur des ventes", "Ventes", 88000, 98000, 1),
    ("Commis d'entrepot", "Entrepot", 41000, 49000, 12),
    ("Chef d'equipe entrepot", "Entrepot", 55000, 63000, 3),
    ("Acheteur", "Approvisionnement", 58000, 70000, 3),
    ("Technicien comptable", "Administration", 50000, 60000, 3),
    ("Coordonnateur marketing", "Marketing", 48000, 58000, 3),
    ("Adjointe administrative", "Administration", 44000, 52000, 4),
    ("Analyste d'affaires", "Administration", 62000, 74000, 1),
    ("Directeur general", "Direction", 125000, 125000, 1),
    ("Controleur financier", "Direction", 95000, 105000, 1),
    ("Livreur", "Entrepot", 43000, 50000, 2),
]

employes = []
mat = 500
for poste, dept, smin, smax, n in POSTES:
    for _ in range(n):
        mat += 1
        embauche = DEBUT - timedelta(days=rng.randint(60, 4200))
        # Roulement plus eleve a l'entrepot : c'est un constat RH du tableau de bord
        proba_depart = 0.28 if dept == "Entrepot" else 0.08
        depart = None
        if rng.random() < proba_depart:
            depart = DEBUT + timedelta(days=rng.randint(90, 700))
        employes.append({
            "matricule": f"EMP-{mat}",
            "prenom": rng.choice(PRENOMS),
            "nom": rng.choice(NOMS_FAM),
            "poste": poste,
            "departement": dept,
            "entrepot": rng.choices([e["code"] for e in ENTREPOTS], weights=[0.45, 0.38, 0.17])[0],
            "date_embauche": embauche,
            "date_depart": depart,
            "salaire_annuel": rng.randint(smin // 1000, smax // 1000) * 1000,
            "statut": rng.choices(["Temps plein", "Temps partiel"], weights=[0.86, 0.14])[0],
        })

# Les departs sont majoritairement remplaces : l'effectif reste stable, mais le
# roulement (surtout a l'entrepot) reste mesurable dans les donnees.
remplacants = []
for e in [x for x in employes if x["date_depart"]]:
    if rng.random() < 0.78:
        mat += 1
        smin, smax = next((a, b) for p_, d_, a, b, n_ in POSTES if p_ == e["poste"])
        remplacants.append({
            "matricule": f"EMP-{mat}",
            "prenom": rng.choice(PRENOMS),
            "nom": rng.choice(NOMS_FAM),
            "poste": e["poste"],
            "departement": e["departement"],
            "entrepot": e["entrepot"],
            "date_embauche": e["date_depart"] + timedelta(days=rng.randint(14, 70)),
            "date_depart": None,
            "salaire_annuel": rng.randint(smin // 1000, smax // 1000) * 1000,
            "statut": e["statut"],
        })
employes.extend(remplacants)

representants = [e for e in employes if e["poste"] == "Representant des ventes"]
for c in clients:
    c["representant"] = rng.choice(representants)["matricule"]

CANAUX = ["Publicite numerique", "Courriel", "Salons professionnels",
          "Catalogue imprime", "Commandite locale"]


# Le fournisseur dont le cout derive doit reellement approvisionner la famille concernee.
code_derive = next(f["code"] for f in fournisseurs if f["nom"] == FOURNISSEUR_DERIVE)
for p in produits:
    if p["famille"] == "Vetements techniques" and rng.random() < 0.62:
        p["fournisseur"] = code_derive

par_sku = {p["sku"]: p for p in produits}
par_famille: dict[str, list] = {}
for p in produits:
    par_famille.setdefault(p["famille"], []).append(p)


def facteur_cout(produit: dict, jour: date) -> float:
    """Inflation generale + derive ciblee sur le fournisseur Nordik a partir de mai 2025."""
    f = 1.0 + (0.021 if jour.year == 2025 else 0.0)
    if produit["fournisseur"] == code_derive and jour >= DEBUT_DERIVE:
        f *= AMPLEUR_DERIVE
    return f


def poids_saison(famille: str, mois: int) -> float:
    saison = FAMILLES[famille]["saison"]
    if not saison:
        return 1.0
    return 2.6 if mois in saison else 0.45


# --- Ventes -----------------------------------------------------------------
# Saisonnalite du grossiste : les detaillants s'approvisionnent AVANT la saison
# de vente au detail (pic aout-novembre pour l'hiver, mars-mai pour l'ete).
SAISON_COMMANDES = {1: 0.62, 2: 0.70, 3: 0.95, 4: 1.15, 5: 1.28, 6: 1.10,
                    7: 0.85, 8: 1.32, 9: 1.55, 10: 1.48, 11: 1.20, 12: 0.72}

poids_clients = [{"A": 9.0, "B": 2.6, "C": 1.0}[c["segment"]] for c in clients]
CANAUX_VENTE = ["Representant", "Telephone", "Portail web", "Courriel", "Salon"]

ventes = []
no_cmd = 100000
jour = DEBUT
while jour <= FIN:
    if jour.weekday() == 6:  # ferme le dimanche
        jour += timedelta(days=1)
        continue
    base = 8.6 * SAISON_COMMANDES[jour.month]
    if jour.weekday() == 5:
        base *= 0.35
    if jour.year == 2025:
        base *= 1.115  # croissance d'activite
    n_cmd = max(0, int(rng.gauss(base, base * 0.28)))

    for _ in range(n_cmd):
        no_cmd += 1
        client = rng.choices(clients, weights=poids_clients)[0]
        remise = {"A": rng.uniform(0.18, 0.26), "B": rng.uniform(0.10, 0.17),
                  "C": rng.uniform(0.02, 0.09)}[client["segment"]]
        n_lignes = rng.choices([1, 2, 3, 4, 5, 6, 7], weights=[18, 24, 22, 15, 11, 6, 4])[0]
        familles_pond = [(f, poids_saison(f, jour.month)) for f in FAMILLES]
        entrepot = rng.choices([e["code"] for e in ENTREPOTS], weights=[0.42, 0.40, 0.18])[0]

        # Delai de paiement : il s'allonge en 2025 (constat DSO du tableau de bord)
        moy_delai = 41 if jour.year == 2024 else 51
        delai = max(8, int(rng.gauss(moy_delai, 13)))
        d_livraison = jour + timedelta(days=rng.randint(2, 9))
        d_paiement = jour + timedelta(days=delai)
        if d_paiement > FIN or rng.random() < 0.035:
            d_paiement = None  # facture encore ouverte

        for _ in range(n_lignes):
            famille = rng.choices([f for f, _ in familles_pond],
                                  weights=[w for _, w in familles_pond])[0]
            produit = rng.choice(par_famille[famille])
            qte = rng.choices([1, 2, 3, 4, 6, 8, 12, 24],
                              weights=[10, 16, 18, 16, 14, 12, 9, 5])[0]
            if client["segment"] == "A":
                qte = int(qte * rng.uniform(1.8, 3.4)) or 1
            prix_net = round(produit["prix_liste"] * (1 - remise), 2)
            cout_u = round(produit["cout_standard"] * facteur_cout(produit, jour), 2)
            ventes.append({
                "no_commande": f"CMD-{no_cmd}",
                "date_commande": jour,
                "date_livraison": d_livraison,
                "date_paiement": d_paiement,
                "client": client["code"],
                "representant": client["representant"],
                "entrepot": entrepot,
                "sku": produit["sku"],
                "quantite": qte,
                "prix_unitaire": prix_net,
                "remise_pct": round(remise * 100, 1),
                "cout_unitaire": cout_u,
                "canal": rng.choices(CANAUX_VENTE, weights=[46, 20, 22, 9, 3])[0],
            })
    jour += timedelta(days=1)

# --- Achats fournisseurs ----------------------------------------------------
prod_par_frn: dict[str, list] = {}
for p in produits:
    prod_par_frn.setdefault(p["fournisseur"], []).append(p)

achats = []
no_achat = 70000
for frn in fournisseurs:
    catalogue = prod_par_frn.get(frn["code"], [])
    if not catalogue:
        continue
    j = DEBUT + timedelta(days=rng.randint(0, 20))
    while j <= FIN:
        no_achat += 1
        n_lignes = rng.randint(1, 5)
        d_prevue = j + timedelta(days=frn["delai_moyen_jours"])
        retard = rng.choices([0, 0, 0, rng.randint(1, 6), rng.randint(7, 25)],
                             weights=[58, 12, 10, 14, 6])[0]
        d_reelle = d_prevue + timedelta(days=retard)
        for _ in range(n_lignes):
            produit = rng.choice(catalogue)
            achats.append({
                "no_achat": f"ACH-{no_achat}",
                "date_commande": j,
                "date_prevue": d_prevue,
                "date_reception": d_reelle if d_reelle <= FIN else None,
                "fournisseur": frn["code"],
                "sku": produit["sku"],
                "quantite": rng.choice([12, 24, 36, 48, 60, 96, 120, 240]),
                "cout_unitaire": round(produit["cout_standard"] * facteur_cout(produit, j), 2),
                "statut": "Recue" if d_reelle <= FIN else "En transit",
            })
        j += timedelta(days=rng.randint(9, 20))

# --- Stock : photo mensuelle par entrepot ------------------------------------
# Saguenay conserve deliberement un stock disproportionne par rapport a ses ventes :
# c'est le probleme de rotation que le tableau de bord doit faire ressortir.
COUVERTURE = {"ENT-QC": 1.0, "ENT-MTL": 0.78, "ENT-SAG": 0.61}
MULT_STOCK = {"ENT-QC": 1.0, "ENT-MTL": 0.85, "ENT-SAG": 2.75}
PART_VENTES = {"ENT-QC": 0.42, "ENT-MTL": 0.40, "ENT-SAG": 0.18}

stock_par_entrepot = {}
for ent in ENTREPOTS:
    n = int(len(produits) * COUVERTURE[ent["code"]])
    stock_par_entrepot[ent["code"]] = rng.sample(produits, k=n)

ventes_qte_sku: dict[str, int] = {}
for v in ventes:
    ventes_qte_sku[v["sku"]] = ventes_qte_sku.get(v["sku"], 0) + v["quantite"]

stocks = []
mois_courant = date(2024, 1, 31)
while mois_courant <= FIN:
    for ent in ENTREPOTS:
        for produit in stock_par_entrepot[ent["code"]]:
            vitesse = ventes_qte_sku.get(produit["sku"], 0) / 24.0 * PART_VENTES[ent["code"]]
            cible = vitesse * 2.2 * MULT_STOCK[ent["code"]]
            saison = poids_saison(produit["famille"], (mois_courant.month % 12) + 1)
            qte = max(0, int(rng.gauss(cible * saison, max(1.0, cible * 0.30))))
            stocks.append({
                "date_photo": mois_courant,
                "entrepot": ent["code"],
                "sku": produit["sku"],
                "quantite": qte,
                "cout_unitaire": round(produit["cout_standard"] * facteur_cout(produit, mois_courant), 2),
                "seuil_min": int(vitesse * 1.1),
            })
    # dernier jour du mois suivant
    y, m = mois_courant.year, mois_courant.month
    m2, y2 = (1, y + 1) if m == 12 else (m + 1, y)
    m3, y3 = (1, y2 + 1) if m2 == 12 else (m2 + 1, y2)
    mois_courant = date(y3, m3, 1) - timedelta(days=1)

# --- Paie mensuelle ---------------------------------------------------------
paie = []
m_courant = date(2024, 1, 1)
while m_courant <= FIN:
    for e in employes:
        if e["date_embauche"] > m_courant:
            continue
        if e["date_depart"] and e["date_depart"] < m_courant:
            continue
        base = e["salaire_annuel"] / 12.0
        if e["statut"] == "Temps partiel":
            base *= 0.6
        if m_courant.year == 2025:
            base *= 1.038  # indexation salariale 2025
        prime = 0.0
        if e["poste"] == "Representant des ventes":
            prime = base * rng.uniform(0.04, 0.22) * SAISON_COMMANDES[m_courant.month]
        heures_supp = 0.0
        if e["departement"] == "Entrepot":
            heures_supp = base * rng.uniform(0.0, 0.18) * SAISON_COMMANDES[m_courant.month]
        brut = base + prime + heures_supp
        paie.append({
            "mois": m_courant,
            "matricule": e["matricule"],
            "salaire_base": round(base, 2),
            "primes": round(prime, 2),
            "heures_supplementaires": round(heures_supp, 2),
            "charges_sociales": round(brut * 0.1435, 2),
            "cout_total": round(brut * 1.1435, 2),
        })
    y, m = m_courant.year, m_courant.month
    m_courant = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)

# --- Marketing --------------------------------------------------------------
PROFIL_CANAL = {
    # (budget min, budget max, prospects par 1000$, taux conversion, mois actifs)
    "Publicite numerique": (4200, 7400, 22, 0.052, list(range(1, 13))),
    "Courriel": (700, 1500, 58, 0.094, list(range(1, 13))),
    "Salons professionnels": (17000, 33000, 2.1, 0.061, [2, 3, 9, 10]),
    "Catalogue imprime": (8500, 14500, 5.4, 0.038, [3, 8]),
    "Commandite locale": (1100, 2600, 6.2, 0.021, list(range(1, 13))),
}

marketing = []
m_courant = date(2024, 1, 1)
while m_courant <= FIN:
    for canal in CANAUX:
        bmin, bmax, pr_par_k, conv, mois_actifs = PROFIL_CANAL[canal]
        if m_courant.month not in mois_actifs:
            continue
        budget = round(rng.uniform(bmin, bmax), 2)
        depense = round(budget * rng.uniform(0.86, 1.14), 2)
        prospects = max(0, int(rng.gauss(depense / 1000 * pr_par_k, 4)))
        marketing.append({
            "mois": m_courant,
            "canal": canal,
            "budget": budget,
            "depense": depense,
            "prospects": prospects,
            "nouveaux_clients": max(0, int(rng.gauss(prospects * conv, 1.2))),
        })
    y, m = m_courant.year, m_courant.month
    m_courant = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)

# --- Charges d'exploitation -------------------------------------------------
PROFIL_CHARGE = {
    "Loyer": (0.0, {"ENT-QC": 14200, "ENT-MTL": 21500, "ENT-SAG": 8900}),
    "Energie": (0.09, {"ENT-QC": 2900, "ENT-MTL": 4100, "ENT-SAG": 2200}),
    "Assurances": (0.02, {"ENT-QC": 1850, "ENT-MTL": 2400, "ENT-SAG": 1200}),
    "Entretien et reparations": (0.22, {"ENT-QC": 1400, "ENT-MTL": 2100, "ENT-SAG": 900}),
    "Telecommunications": (0.05, {"ENT-QC": 620, "ENT-MTL": 780, "ENT-SAG": 410}),
    "Logiciels et TI": (0.04, {"ENT-QC": 3100, "ENT-MTL": 0, "ENT-SAG": 0}),
    "Honoraires professionnels": (0.35, {"ENT-QC": 2600, "ENT-MTL": 0, "ENT-SAG": 0}),
    "Fournitures de bureau": (0.18, {"ENT-QC": 540, "ENT-MTL": 610, "ENT-SAG": 300}),
    "Transport et livraison": (0.14, {"ENT-QC": 9800, "ENT-MTL": 11900, "ENT-SAG": 4300}),
}

charges = []
m_courant = date(2024, 1, 1)
while m_courant <= FIN:
    for categorie, (variabilite, par_ent) in PROFIL_CHARGE.items():
        for code_ent, montant_base in par_ent.items():
            if montant_base == 0:
                continue
            saison = SAISON_COMMANDES[m_courant.month] if categorie == "Transport et livraison" else 1.0
            inflation = 1.0 + (0.034 if m_courant.year == 2025 else 0.0)
            montant = montant_base * saison * inflation * (1 + rng.uniform(-variabilite, variabilite))
            charges.append({
                "mois": m_courant,
                "categorie": categorie,
                "entrepot": code_ent,
                "montant": round(montant, 2),
            })
    y, m = m_courant.year, m_courant.month
    m_courant = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)


# ---------------------------------------------------------------------------
# Degradation volontaire + ecriture des fichiers sources
# ---------------------------------------------------------------------------
# Les referentiels ci-dessus sont construits sans accents pour rester manipulables ;
# on les reintroduit a l'ecriture, ce qui rend le probleme d'encodage reel
# (l'ERP exporte en cp1252, la comptabilite en latin-1, le CRM en UTF-8).

ACCENTS = {
    "Quebec": "Québec", "Montreal": "Montréal", "Levis": "Lévis",
    "Trois-Rivieres": "Trois-Rivières", "Saint-Jerome": "Saint-Jérôme",
    "Sept-Iles": "Sept-Îles", "Rimouski": "Rimouski",
    "Randonnee": "Randonnée", "Vetements techniques": "Vêtements techniques",
    "Peche": "Pêche",
    "Energie": "Énergie", "Entretien et reparations": "Entretien et réparations",
    "Telecommunications": "Télécommunications",
    "Detaillant independant": "Détaillant indépendant",
    "Chaine regionale": "Chaîne régionale",
    "Cooperative de plein air": "Coopérative de plein air",
    "Saguenay-Lac-Saint-Jean": "Saguenay–Lac-Saint-Jean",
    "Representant des ventes": "Représentant des ventes",
    "Commis d'entrepot": "Commis d'entrepôt", "Chef d'equipe entrepot": "Chef d'équipe entrepôt",
    "Directeur general": "Directeur général", "Controleur financier": "Contrôleur financier",
    "Entrepot": "Entrepôt",
    "Publicite numerique": "Publicité numérique", "Catalogue imprime": "Catalogue imprimé",
    "Representant": "Représentant", "Telephone": "Téléphone",
}
acc = lambda s: ACCENTS.get(s, s)

MOIS_ABR = {1: "janv", 2: "févr", 3: "mars", 4: "avr", 5: "mai", 6: "juin",
            7: "juil", 8: "août", 9: "sept", 10: "oct", 11: "nov", 12: "déc"}


def dec_fr(x: float) -> str:
    """Decimale a la francaise, comme l'exporte un ERP configure en francais."""
    return f"{x:.2f}".replace(".", ",")


def date_multi(d, i: int) -> str:
    """L'ERP a change de format d'export deux fois en deux ans."""
    if d is None:
        return ""
    r = i % 10
    if r < 7:
        return d.strftime("%d/%m/%Y")
    if r < 9:
        return d.strftime("%Y-%m-%d")
    return f"{d.day:02d}-{MOIS_ABR[d.month]}-{str(d.year)[2:]}"


# --- 1 & 2. ERP ventes (CSV point-virgule, cp1252, decimale virgule) ---------
# On conserve l'annee reelle a cote de la ligne : le decoupage en deux fichiers
# annuels doit rester correct meme apres avoir casse les dates.
erp = []
for i, v in enumerate(ventes):
    erp.append([v["date_commande"].year, {
        "NO COMMANDE": v["no_commande"],
        "DATE COMMANDE": date_multi(v["date_commande"], i),
        "DATE LIVRAISON": date_multi(v["date_livraison"], i + 3),
        "DATE PAIEMENT": date_multi(v["date_paiement"], i + 6),
        "CODE CLIENT": v["client"],
        "REPRESENTANT": v["representant"],
        "ENTREPOT": v["entrepot"],
        "CODE ARTICLE": v["sku"],
        "QTE": str(v["quantite"]),
        "PRIX UNITAIRE": dec_fr(v["prix_unitaire"]),
        "REMISE %": dec_fr(v["remise_pct"]),
        "COUT UNITAIRE": dec_fr(v["cout_unitaire"]),
        "CANAL DE VENTE": acc(v["canal"]),
    }])

ordre = list(range(len(erp)))
rng.shuffle(ordre)
curseur = 0


def prendre(k: int) -> list[int]:
    """Distribue des lignes distinctes a chaque type d'anomalie (pas de recouvrement)."""
    global curseur
    part = ordre[curseur:curseur + k]
    curseur += k
    return part


for i in prendre(92):                      # dates inexploitables
    erp[i][1]["DATE COMMANDE"] = rng.choice(["31/02/2024", "", "00/00/0000", "n/d"])
compter("ventes_date_invalide", 92)

for i in prendre(58):                      # article absent du catalogue
    erp[i][1]["CODE ARTICLE"] = f"BD-{rng.randint(9000, 9999)}"
compter("ventes_sku_orphelin", 58)

for i in prendre(47):                      # quantite nulle ou negative
    erp[i][1]["QTE"] = str(rng.choice([0, -1, -2, -6]))
compter("ventes_quantite_invalide", 47)

for i in prendre(31):                      # prix a zero
    erp[i][1]["PRIX UNITAIRE"] = "0,00"
compter("ventes_prix_zero", 31)

for i in prendre(26):                      # virgule oubliee a la saisie (x1000)
    erp[i][1]["PRIX UNITAIRE"] = dec_fr(float(erp[i][1]["PRIX UNITAIRE"].replace(",", ".")) * 1000)
compter("ventes_prix_aberrant", 26)

for i in prendre(134):                     # canal de vente non saisi
    erp[i][1]["CANAL DE VENTE"] = rng.choice(["", " ", "N/A"])
compter("ventes_canal_manquant", 134)

for i in prendre(210):                     # espaces parasites et casse incoherente
    code = erp[i][1]["CODE CLIENT"]
    erp[i][1]["CODE CLIENT"] = rng.choice([f"  {code}", f"{code} ", code.lower()])
compter("ventes_code_client_sale", 210)

for i in prendre(186):                     # meme lot importe deux fois dans l'ERP
    erp.append([erp[i][0], dict(erp[i][1])])
compter("ventes_doublons", 186)

rng.shuffle(erp)
COLS_ERP = list(erp[0][1].keys())
for annee in (2024, 2025):
    with open(os.path.join(BRUT, f"erp_ventes_{annee}.csv"),
              "w", encoding="cp1252", newline="", errors="replace") as f:
        w = csv.DictWriter(f, fieldnames=COLS_ERP, delimiter=";")
        w.writeheader()
        for an, lg in erp:
            if an == annee:
                w.writerow(lg)
        # Pied de page ajoute par l'outil d'export : ce ne sont pas des lignes de donnees.
        f.write("\n")
        f.write("TOTAL GENERAL" + ";" * (len(COLS_ERP) - 1) + "\n")
        f.write(f"Export du {FIN.strftime('%d/%m/%Y')} - Boréal Distribution inc."
                + ";" * (len(COLS_ERP) - 1) + "\n")
compter("ventes_lignes_pied_de_page", 4)

# --- 3. CRM clients (JSON imbrique, UTF-8) ----------------------------------
VARIANTES_PROV = {"QC": ["QC", "Québec", "Quebec", "qc"], "ON": ["ON", "Ontario", "on"],
                  "NB": ["NB", "Nouveau-Brunswick"], "NS": ["NS", "Nouvelle-Écosse"],
                  "PE": ["PE", "Île-du-Prince-Édouard"]}

fiches = []
n_ville_sale = n_prov_variante = 0
for c in clients:
    ville = acc(c["ville"])
    ville_ecrite = rng.choice([ville, ville.upper(), f"{ville} ", ville.lower()])
    province_ecrite = rng.choice(VARIANTES_PROV[c["province"]])
    n_ville_sale += ville_ecrite != ville
    n_prov_variante += province_ecrite != c["province"]
    fiches.append({
        "identification": {
            "code": c["code"],
            "raison_sociale": c["nom"],
            "type_commerce": acc(c["type"]),
            "date_ouverture_compte": c["date_ouverture"].isoformat(),
        },
        "adresse": {
            "ville": ville_ecrite,
            "province": province_ecrite,
            "code_postal": c["code_postal"],
        },
        "commercial": {
            "segment": c["segment"],
            "conditions_paiement": c["conditions_paiement"],
            "representant_matricule": c["representant"],
            "courriel": c["courriel"],
        },
    })
compter("clients_province_variantes", n_prov_variante)
compter("clients_ville_casse", n_ville_sale)

n_courriel_invalide = n_courriel_vide = 0
for f_ in rng.sample(fiches, 19):
    valeur = rng.choice(["", "n/a", "achats@", "a completer", None])
    f_["commercial"]["courriel"] = valeur
    if valeur:
        n_courriel_invalide += 1
    else:
        n_courriel_vide += 1
compter("clients_courriel_invalide", n_courriel_invalide)
compter("clients_courriel_vide", n_courriel_vide)

for f_ in rng.sample(fiches, 13):
    f_["adresse"]["code_postal"] = rng.choice(["", None, "  "])
compter("clients_code_postal_manquant", 13)

# Doublons metier : meme entreprise saisie deux fois sous un code different.
suivant = 900
for orig in rng.sample(fiches, 14):
    suivant += 1
    copie = json.loads(json.dumps(orig))
    copie["identification"]["code"] = f"CLI-{suivant}"
    copie["identification"]["raison_sociale"] = orig["identification"]["raison_sociale"].upper()
    fiches.append(copie)
compter("clients_doublons_metier", 14)
rng.shuffle(fiches)

with open(os.path.join(BRUT, "crm_clients.json"), "w", encoding="utf-8") as f:
    json.dump({"exporte_le": FIN.isoformat(), "source": "CRM Boréal v4", "clients": fiches},
              f, ensure_ascii=False, indent=1)


# --- 4. RH (classeur Excel a deux feuilles, en-tete precede de lignes de titre) ---
from openpyxl import Workbook

wb = Workbook()
# openpyxl horodate le classeur a la creation : sans cela, le seul fichier non
# reproductible du pipeline serait ce .xlsx, dont le contenu est pourtant identique
# d'une execution a l'autre. On fige les proprietes du document.
wb.properties.creator = "Extraction RH — Boréal Distribution inc."
wb.properties.lastModifiedBy = wb.properties.creator
wb.properties.created = datetime(FIN.year, FIN.month, FIN.day, 8, 0, 0)
wb.properties.modified = wb.properties.created
ws = wb.active
ws.title = "Employés"
ws.append(["BORÉAL DISTRIBUTION INC."])
ws.append([f"Liste du personnel - extraction du {FIN.strftime('%d/%m/%Y')}"])
ws.append([])
ws.append(["Matricule", "Prénom", "Nom", "Poste", "Département", "Entrepôt",
           "Date d'embauche", "Date de départ", "Salaire annuel", "Statut", ""])

lignes_rh = list(employes)
for e in rng.sample(employes, 2):          # employe saisi deux fois
    lignes_rh.append(dict(e))
compter("rh_doublons", 2)
rng.shuffle(lignes_rh)

n_salaire_texte = 0
for i, e in enumerate(lignes_rh):
    if i % 3 != 0:                         # majorite des salaires saisis en texte
        salaire = f"{e['salaire_annuel']:,}".replace(",", " ") + " $"
        n_salaire_texte += 1
    else:
        salaire = e["salaire_annuel"]
    embauche = e["date_embauche"].strftime("%d/%m/%Y") if i % 2 else e["date_embauche"]
    depart = ""
    if e["date_depart"]:
        depart = e["date_depart"].strftime("%Y-%m-%d") if i % 2 else e["date_depart"]
    ws.append([e["matricule"], e["prenom"], e["nom"], acc(e["poste"]), acc(e["departement"]),
               e["entrepot"], embauche, depart, salaire, e["statut"], ""])
compter("rh_salaire_en_texte", n_salaire_texte)

ws.append([])
ws.append(["TOTAL", "", "", "", "", "", "", "",
           sum(e["salaire_annuel"] for e in lignes_rh), "", ""])
compter("rh_ligne_total", 1)

ws2 = wb.create_sheet("Paie mensuelle")
ws2.append(["Mois", "Matricule", "Salaire de base", "Primes", "Heures supplémentaires",
            "Charges sociales", "Coût total"])
for p in paie:
    ws2.append([p["mois"].strftime("%Y-%m"), p["matricule"], p["salaire_base"], p["primes"],
                p["heures_supplementaires"], p["charges_sociales"], p["cout_total"]])

CHEMIN_RH = os.path.join(BRUT, "rh_employes.xlsx")
wb.save(CHEMIN_RH)


def figer_classeur(chemin: str, horodatage=(2025, 12, 31, 8, 0, 0)) -> None:
    """
    Rend le .xlsx reproductible au bit pres.

    Un classeur Excel est une archive ZIP : chaque entree porte l'heure a laquelle
    elle a ete ecrite, et openpyxl reecrit en plus la propriete 'modified' du
    document a chaque enregistrement. Deux executions produisant des donnees
    strictement identiques donnaient donc deux fichiers differents. On reconstruit
    l'archive avec des entrees triees et horodatees a une date fixe.
    """
    import zipfile
    horodatage_iso = ("%04d-%02d-%02dT%02d:%02d:%02dZ" % horodatage)
    tampon = chemin + ".tmp"
    with zipfile.ZipFile(chemin) as source, \
            zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as cible:
        for nom in sorted(source.namelist()):
            contenu = source.read(nom)
            if nom == "docProps/core.xml":
                contenu = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)",
                                 rb"\g<1>" + horodatage_iso.encode() + rb"\g<2>", contenu)
            entree = zipfile.ZipInfo(nom, date_time=horodatage)
            entree.compress_type = zipfile.ZIP_DEFLATED
            entree.external_attr = 0o600 << 16
            cible.writestr(entree, contenu)
    os.replace(tampon, chemin)


figer_classeur(CHEMIN_RH)

# --- 5. Achats fournisseurs (CSV tabulation, montants avec symbole et espace insecable) ---
lignes_achats = []
for a in achats:
    lignes_achats.append({
        "no_achat": a["no_achat"],
        "date_commande": a["date_commande"].isoformat(),
        "date_prevue": a["date_prevue"].isoformat(),
        "date_reception": a["date_reception"].isoformat() if a["date_reception"] else "",
        "code_fournisseur": a["fournisseur"],
        "code_article": a["sku"],
        "quantite": str(a["quantite"]),
        "cout_unitaire": f"{a['cout_unitaire']:,.2f}".replace(",", " ").replace(".", ",") + " $",
        "statut": a["statut"],
    })

ordre_a = list(range(len(lignes_achats)))
rng.shuffle(ordre_a)
for i in ordre_a[:38]:                     # retours fournisseur saisis en negatif
    lignes_achats[i]["quantite"] = str(-abs(int(lignes_achats[i]["quantite"])) // 4 or -6)
compter("achats_quantite_negative", 38)
for i in ordre_a[38:63]:                   # article absent du catalogue
    lignes_achats[i]["code_article"] = f"BD-{rng.randint(9000, 9999)}"
compter("achats_sku_orphelin", 25)

with open(os.path.join(BRUT, "achats_fournisseurs.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes_achats[0].keys()), delimiter="\t")
    w.writeheader()
    w.writerows(lignes_achats)

# --- 6. Stock (CSV virgule, UTF-8, decimale point) ---------------------------
lignes_stock = [{
    "date_photo": s["date_photo"].isoformat(),
    "code_entrepot": s["entrepot"],
    "code_article": s["sku"],
    "quantite_en_stock": str(s["quantite"]),
    "cout_unitaire": f"{s['cout_unitaire']:.2f}",
    "seuil_minimum": str(s["seuil_min"]),
} for s in stocks]

ordre_s = list(range(len(lignes_stock)))
rng.shuffle(ordre_s)
for i in ordre_s[:52]:
    lignes_stock[i]["code_article"] = f"BD-{rng.randint(9000, 9999)}"
compter("stock_sku_orphelin", 52)
for i in ordre_s[52:81]:                   # ecarts d'inventaire saisis en negatif
    lignes_stock[i]["quantite_en_stock"] = str(-rng.randint(1, 9))
compter("stock_quantite_negative", 29)
for i in ordre_s[81:145]:                  # photo dupliquee (script d'extraction relance)
    lignes_stock.append(dict(lignes_stock[i]))
compter("stock_doublons", 64)
rng.shuffle(lignes_stock)

with open(os.path.join(BRUT, "stock_inventaire.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes_stock[0].keys()))
    w.writeheader()
    w.writerows(lignes_stock)

# --- 7. Marketing (JSON, horodatages avec fuseau, montants en texte) ---------
enr_marketing = []
for i, m in enumerate(marketing):
    enr_marketing.append({
        "periode": m["mois"].isoformat() + "T00:00:00-05:00",
        "canal": acc(m["canal"]),
        "budget_prevu": None if i % 17 == 0 else m["budget"],
        "depense_reelle": f"{m['depense']:,.2f}".replace(",", " ").replace(".", ",") + " $",
        "prospects_generes": m["prospects"],
        "nouveaux_clients": m["nouveaux_clients"],
    })
compter("marketing_budget_manquant", sum(1 for e in enr_marketing if e["budget_prevu"] is None))

with open(os.path.join(BRUT, "marketing_campagnes.json"), "w", encoding="utf-8") as f:
    json.dump({"systeme": "Suivi campagnes - export manuel", "campagnes": enr_marketing},
              f, ensure_ascii=False, indent=1)

# --- 8. Charges d'exploitation (CSV point-virgule, latin-1, decimale virgule) ---
lignes_charges = []
n_cat_casse = 0
for c in charges:
    canonique = acc(c["categorie"])
    ecrite = rng.choice([canonique, canonique.upper(), canonique.lower()])
    n_cat_casse += ecrite != canonique
    lignes_charges.append({"Mois": c["mois"].strftime("%m/%Y"), "Categorie": ecrite,
                           "Entrepot": c["entrepot"], "Montant": dec_fr(c["montant"])})
compter("charges_categorie_casse", n_cat_casse)

for i in rng.sample(range(len(lignes_charges)), 17):   # ecriture comptable saisie deux fois
    lignes_charges.append(dict(lignes_charges[i]))
compter("charges_doublons", 17)
rng.shuffle(lignes_charges)

with open(os.path.join(BRUT, "compta_charges.csv"), "w", encoding="latin-1",
          newline="", errors="replace") as f:
    w = csv.DictWriter(f, fieldnames=["Mois", "Categorie", "Entrepot", "Montant"], delimiter=";")
    w.writeheader()
    w.writerows(lignes_charges)

# --- 9. Referentiels produits et fournisseurs -------------------------------
lignes_cat = [{
    "sku": p["sku"], "designation": p["nom"], "famille": acc(p["famille"]),
    "code_fournisseur": p["fournisseur"], "cout_standard": dec_fr(p["cout_standard"]),
    "prix_liste": dec_fr(p["prix_liste"]), "poids_kg": dec_fr(p["poids_kg"]),
} for p in produits]

for i in rng.sample(range(len(lignes_cat)), 5):        # cout standard jamais renseigne
    lignes_cat[i]["cout_standard"] = "0,00"
compter("catalogue_cout_zero", 5)
for i in rng.sample(range(len(lignes_cat)), 8):        # SKU present deux fois au catalogue
    lignes_cat.append(dict(lignes_cat[i]))
compter("catalogue_doublons", 8)

with open(os.path.join(BRUT, "catalogue_produits.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes_cat[0].keys()))
    w.writeheader()
    w.writerows(lignes_cat)

with open(os.path.join(BRUT, "fournisseurs.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["code", "nom", "pays", "delai_moyen_jours", "conditions"])
    w.writeheader()
    w.writerows(fournisseurs)

with open(os.path.join(BRUT, "entrepots.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["code", "nom", "region", "surface_m2"])
    w.writeheader()
    for e in ENTREPOTS:
        w.writerow({**e, "nom": acc(e["nom"]), "region": acc(e["region"])})

# --- Journal des anomalies injectees ----------------------------------------
with open(os.path.join(BRUT, "_anomalies_injectees.json"), "w", encoding="utf-8") as f:
    json.dump({"seed": RANDOM_SEED, "anomalies": dict(sorted(INJECTE.items())),
               "total": sum(INJECTE.values())}, f, ensure_ascii=False, indent=1)

print("Sources brutes generees dans data/brut/")
print(f"  ventes ERP        : {len(erp):>7} lignes (dont {INJECTE['ventes_doublons']} doublons)")
print(f"  clients CRM       : {len(fiches):>7} fiches")
print(f"  employes RH       : {len(lignes_rh):>7} lignes + {len(paie)} lignes de paie")
print(f"  achats            : {len(lignes_achats):>7} lignes")
print(f"  stock             : {len(lignes_stock):>7} photos")
print(f"  marketing         : {len(enr_marketing):>7} lignes")
print(f"  charges           : {len(lignes_charges):>7} ecritures")
print(f"  catalogue         : {len(lignes_cat):>7} articles")
print(f"  anomalies injectees : {sum(INJECTE.values())}")
