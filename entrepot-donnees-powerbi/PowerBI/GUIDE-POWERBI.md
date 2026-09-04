# Construire le rapport Power BI

Ce guide reconstruit le rapport à partir de zéro, à partir des CSV de `data/powerbi/`.
Compter environ 45 minutes la première fois.

---

## 1. Importer les tables

Power BI Desktop n'a pas de connecteur natif pour SQLite ; l'import se fait donc
depuis les CSV exportés par `Python/5_exporter_powerbi.py`.

**Accueil → Obtenir les données → Texte/CSV**, puis répéter pour les 14 fichiers de
`data/powerbi/`. Dans la fenêtre d'aperçu, vérifier avant de charger :

| Paramètre | Valeur attendue | Ce qui arrive si c'est faux |
|---|---|---|
| Origine du fichier | `65001: Unicode (UTF-8)` | `Vêtements techniques` devient `VÃªtements techniques` |
| Délimiteur | Virgule | Toute la ligne atterrit dans une seule colonne |
| Détection du type de données | Sur les 200 premières lignes | Une colonne majoritairement vide en tête de fichier est typée en texte |

Les fichiers sont écrits en UTF-8 **avec BOM** précisément pour que Power BI
sélectionne le bon encodage tout seul. S'il propose autre chose que 65001, corriger
à la main avant de charger.

### Vérifications dans Power Query

Avant `Fermer et appliquer` :

- `dim_date[date]`, `dim_employe[date_embauche]`, `dim_employe[date_depart]`,
  `dim_client[date_ouverture]` doivent être de type **Date** (pas Texte).
- Toutes les colonnes de montants (`montant_ht`, `cout_total`, `marge`, `valeur_stock`,
  `montant`, `depense`, `budget`, `cout_total` de la paie) doivent être en
  **Nombre décimal**. Si l'une est en Texte, l'export a été ouvert et réenregistré
  par Excel entre-temps — réexporter plutôt que corriger dans Power Query.
- Les colonnes `*_id` doivent être en **Nombre entier**. Une clé typée en texte
  crée une relation qui fonctionne mais ralentit tout le modèle.

### Désactiver la date/heure automatique — à faire en premier

**Fichier → Options → Chargement des données → décocher « Date/heure automatique
pour les nouveaux fichiers »**.

Laissée active, cette option crée une table de dates masquée **pour chaque colonne
de date du modèle** — soit une dizaine ici. Le fichier gonfle, et surtout les
fonctions de time intelligence se mettent à référencer ces tables fantômes au lieu
de `dim_date`, ce qui donne des comparaisons annuelles fausses sans aucun message
d'erreur.

---

## 2. Créer les relations

**Modélisation → Gérer les relations.** Toutes en cardinalité **un à plusieurs**
(la dimension vers le fait) et en sens de filtre **unique**.

| Depuis | Vers | État |
|---|---|---|
| `dim_date[date_id]` | `fait_ventes[date_commande_id]` | **Active** |
| `dim_date[date_id]` | `fait_ventes[date_livraison_id]` | Inactive |
| `dim_date[date_id]` | `fait_ventes[date_paiement_id]` | Inactive |
| `dim_client[client_id]` | `fait_ventes[client_id]` | Active |
| `dim_produit[produit_id]` | `fait_ventes[produit_id]` | Active |
| `dim_entrepot[entrepot_id]` | `fait_ventes[entrepot_id]` | Active |
| `dim_employe[employe_id]` | `fait_ventes[employe_id]` | Active |
| `dim_date[date_id]` | `fait_achats[date_commande_id]` | **Active** |
| `dim_date[date_id]` | `fait_achats[date_reception_id]` | Inactive |
| `dim_fournisseur[fournisseur_id]` | `fait_achats[fournisseur_id]` | Active |
| `dim_produit[produit_id]` | `fait_achats[produit_id]` | Active |
| `dim_date[date_id]` | `fait_stock[date_id]` | Active |
| `dim_entrepot[entrepot_id]` | `fait_stock[entrepot_id]` | Active |
| `dim_produit[produit_id]` | `fait_stock[produit_id]` | Active |
| `dim_date[date_id]` | `fait_paie[date_id]` | Active |
| `dim_employe[employe_id]` | `fait_paie[employe_id]` | Active |
| `dim_date[date_id]` | `fait_marketing[date_id]` | Active |
| `dim_canal_marketing[canal_id]` | `fait_marketing[canal_id]` | Active |
| `dim_date[date_id]` | `fait_charges[date_id]` | Active |
| `dim_entrepot[entrepot_id]` | `fait_charges[entrepot_id]` | Active |
| `dim_fournisseur[code]` | `dim_produit[fournisseur_code]` | Active |

Trois points méritent une explication.

**Une seule relation active entre deux tables.** `fait_ventes` porte trois dates
(commande, livraison, paiement). Power BI n'autorise qu'un seul chemin actif entre
deux tables : les deux autres restent inactives et ne s'activent qu'à la demande,
dans une mesure, avec `USERELATIONSHIP`. La mesure `CA encaissé` en est l'exemple.
C'est ce qui permet de lire le même chiffre d'affaires selon la date de commande ou
selon la date d'encaissement, sans dupliquer la table de dates.

**Le sens de filtre reste unique partout.** `dim_produit` et `dim_entrepot` filtrent
chacune trois tables de faits. Passer une seule relation en bidirectionnel ouvre des
chemins de filtrage ambigus : Power BI refuse alors certaines relations, ou pire, en
choisit une silencieusement.

**`dim_fournisseur → dim_produit` est une relation entre deux dimensions** (modèle
en flocon). Elle est indispensable : c'est elle qui permet de remonter d'une vente
jusqu'au fournisseur de l'article, alors qu'aucune source ne contient ce lien
directement. C'est exactement ce que le schéma en étoile apporte ici.

**`qualite_rejets` ne se relie à rien**, volontairement : cette table décrit des
lignes *écartées*, elle n'a donc pas le même grain que les faits chargés. La relier
à `dim_date` laisserait croire qu'on peut croiser des rejets avec du chiffre
d'affaires — ce qui n'a pas de sens.

---

## 3. Marquer la table de dates

**Sélectionner `dim_date` → Outils de table → Marquer comme table de dates →
colonne `date`.**

Sans cette étape, `SAMEPERIODLASTYEAR`, `TOTALYTD` et `DATEADD` retournent des
résultats faux ou vides. Noter que les *relations* passent par `date_id` (entier)
alors que le *marquage* porte sur `date` (date réelle) : les deux coexistent sans
problème, et c'est la configuration recommandée (jointure sur entier, time
intelligence sur date).

Trier ensuite `dim_date[nom_mois]` par `dim_date[mois]`
(**Outils de colonne → Trier par colonne**), sinon les mois s'affichent dans
l'ordre alphabétique : août, avril, décembre…

---

## 4. Créer les mesures

Coller les mesures de [`mesures.dax`](./mesures.dax) dans l'ordre du fichier
(**Modélisation → Nouvelle mesure**) : plusieurs en référencent d'autres définies
plus haut.

Les regrouper ensuite dans une table de mesures dédiée (**Accueil → Entrer des
données**, table vide nommée `_Mesures`, puis déplacer chaque mesure via
**Table de départ**). Cela évite de chercher une mesure au milieu des colonnes
d'une table de faits.

Formater dès la création : montants en `$ français (Canada)` sans décimale, taux
en pourcentage à une décimale. Un format posé sur la mesure se propage à tous les
visuels ; un format posé sur le visuel est à refaire à chaque fois.

---

## 5. Les pages du rapport

### Page 1 — Direction

| Zone | Visuel | Champs |
|---|---|---|
| Bandeau | 5 cartes | `Chiffre d'affaires`, `Croissance CA %`, `Taux de marge brute`, `Écart de taux de marge (pts)`, `Résultat d'exploitation` |
| Centre | Graphique en courbes | Axe `dim_date[nom_mois]`, valeurs `Chiffre d'affaires`, légende `dim_date[annee]` |
| Droite | Graphique en barres groupées | Axe `dim_produit[famille]`, valeurs `Taux de marge brute` par année |
| Bas | Segments | `dim_date[annee]`, `dim_entrepot[nom]`, `dim_produit[famille]` |

La carte `Écart de taux de marge (pts)` est le cœur de la page : c'est le seul
indicateur qui contredit la lecture optimiste des quatre autres.

### Page 2 — Rentabilité et fournisseurs

| Visuel | Champs |
|---|---|
| Tableau | `dim_fournisseur[nom]`, `Chiffre d'affaires`, `Coût unitaire moyen`, `Variation du coût unitaire %`, `Manque à gagner sur coût d'achat` |
| Barres horizontales | `dim_produit[famille]` × `Écart de taux de marge (pts)`, trié croissant |
| Nuage de points | X `Variation du coût unitaire %`, Y `Taux de marge brute`, taille `Chiffre d'affaires`, détails `dim_fournisseur[nom]` |
| Carte | `Manque à gagner sur coût d'achat` |

Mise en forme conditionnelle sur `Variation du coût unitaire %` : rouge au-delà de
+5 %. C'est ce qui fait ressortir le fournisseur en cause sans avoir à le chercher.

### Page 3 — Clients et encaissement

| Visuel | Champs |
|---|---|
| Barres + courbe cumulée (Pareto) | Axe `dim_client[nom]` (top 15), barres `Chiffre d'affaires`, courbe part cumulée |
| Carte | `Part des 10 premiers clients` |
| Carte géographique | `dim_client[ville]`, taille `Chiffre d'affaires` |
| Courbe | `Délai moyen d'encaissement` par mois |
| Carte | `Encours non réglé` |
| Matrice | Lignes `dim_client[segment]`, colonnes `dim_date[annee]`, valeurs `Chiffre d'affaires` et `Délai moyen d'encaissement` |

### Page 4 — Stocks et approvisionnement

| Visuel | Champs |
|---|---|
| Barres | `dim_entrepot[nom]` × `Rotation des stocks` |
| Barres | `dim_entrepot[nom]` × `Jours de stock` |
| Courbe | `Stock fin de période` par mois, légende `dim_entrepot[nom]` |
| Carte | `Articles sous le seuil` |
| Tableau | `dim_fournisseur[nom]`, `Taux de retard fournisseur`, `Retard moyen (jours)`, `Montant des achats` |

### Page 5 — Coûts et personnel

| Visuel | Champs |
|---|---|
| Graphique en cascade | `Marge brute` → `Masse salariale` → `Charges d'exploitation` → `Dépense marketing` → `Résultat d'exploitation` |
| Anneau | `fait_charges[categorie]` × `Charges d'exploitation` |
| Barres | `dim_canal_marketing[canal]` × `Coût par nouveau client`, trié croissant |
| Courbe et barres | Barres `Masse salariale`, courbe `Masse salariale / CA`, axe année |
| Tableau | `dim_employe[departement]`, `Effectif actif`, `Départs`, `Taux de roulement` |

### Page 6 — Qualité des données

| Visuel | Champs |
|---|---|
| Cartes | `Lignes rejetées`, `Valeurs corrigées`, `Taux de retenue des ventes` |
| Barres horizontales | `qualite_rejets[motif]` × nombre de lignes |
| Matrice | Lignes `qualite_rejets[source]`, colonnes `qualite_rejets[action]` |
| Tableau détaillé | `source`, `cle`, `champ`, `valeur`, `motif`, `action` |

Cette page n'est pas un décor. Un tableau de bord qui n'affiche jamais ce qu'il a
écarté demande une confiance aveugle : ici, chaque ligne rejetée est consultable
avec sa valeur d'origine.

---

## 6. Vérifier que le modèle est juste

Régler les segments sur **2025, aucun autre filtre**, et comparer aux valeurs de
[`../data/ANALYSE.md`](../data/ANALYSE.md), produites indépendamment en SQL :

| Mesure | Valeur attendue (2025) |
|---|---|
| `Chiffre d'affaires` | 17 463 307 $ |
| `Taux de marge brute` | 27,9 % |
| `Écart de taux de marge (pts)` | −3,9 pts |
| `Résultat d'exploitation` | 619 340 $ |
| `Nombre de commandes` | 2 789 |
| `Panier moyen` | 6 261 $ |
| `Part des 10 premiers clients` (toutes années) | 32,2 % |
| `Délai moyen d'encaissement` | 50,3 j |
| `Rotation des stocks` (Saguenay) | 2,75 |
| `Rotation des stocks` (Montréal) | 7,62 |

Un écart signale presque toujours l'une de ces trois causes, dans cet ordre de
fréquence :

1. **La date/heure automatique est restée activée** — les comparaisons annuelles
   passent par une table fantôme.
2. **Une relation a été créée sur la mauvaise colonne de date** — le CA se déplace
   de quelques semaines et la saisonnalité paraît décalée.
3. **`Stock moyen` a été remplacé par une somme** — la rotation est alors divisée
   par le nombre de mois affichés.

---

## 7. Publier

**Accueil → Publier** vers un espace de travail Power BI Service. Les CSV étant des
fichiers locaux, l'actualisation planifiée exige une passerelle de données
(*on-premises data gateway*) pointant vers le dossier. Sans passerelle, le rapport
publié reste consultable mais figé sur les données du dernier import.

Pour une actualisation automatique sans passerelle, il faudrait charger l'entrepôt
dans une base accessible en ligne (PostgreSQL managé, Azure SQL) plutôt que dans un
fichier — le schéma en étoile du projet s'y transpose sans modification, c'est
précisément l'intérêt d'avoir gardé le DDL en SQL portable.
