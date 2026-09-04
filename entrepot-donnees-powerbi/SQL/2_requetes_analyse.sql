-- =============================================================================
-- Boréal Distribution — requêtes d'analyse
--
-- Ces requêtes produisent les chiffres cités dans le README. Elles servent aussi
-- de contre-vérification indépendante des mesures DAX du rapport Power BI :
-- si une mesure DAX et la requête SQL correspondante ne donnent pas le même
-- résultat, c'est la mesure qui est fausse.
--
-- Exécutées par Python/4_analyser.py, qui repère chaque bloc grâce au marqueur
-- « -- @nom ». Elles restent exécutables telles quelles dans n'importe quel
-- client SQLite.
-- =============================================================================


-- @resultat_par_annee
-- Compte de résultat simplifié. Sépare marge brute (ventes - coût des marchandises)
-- et résultat d'exploitation (marge brute - masse salariale - charges - marketing).
WITH ventes AS (
    SELECT d.annee,
           SUM(v.montant_ht) AS ca,
           SUM(v.cout_total) AS cout_marchandises,
           COUNT(DISTINCT v.no_commande) AS nb_commandes,
           COUNT(*) AS nb_lignes
    FROM fait_ventes v
    JOIN dim_date d ON d.date_id = v.date_commande_id
    GROUP BY d.annee
),
salaires AS (
    SELECT d.annee, SUM(p.cout_total) AS masse_salariale
    FROM fait_paie p JOIN dim_date d ON d.date_id = p.date_id
    GROUP BY d.annee
),
frais AS (
    SELECT d.annee, SUM(c.montant) AS charges
    FROM fait_charges c JOIN dim_date d ON d.date_id = c.date_id
    GROUP BY d.annee
),
pub AS (
    SELECT d.annee, SUM(m.depense) AS marketing
    FROM fait_marketing m JOIN dim_date d ON d.date_id = m.date_id
    GROUP BY d.annee
)
SELECT v.annee,
       ROUND(v.ca, 0)                                              AS ca,
       v.nb_commandes,
       ROUND(v.ca / v.nb_commandes, 0)                             AS panier_moyen,
       ROUND(v.ca - v.cout_marchandises, 0)                        AS marge_brute,
       ROUND(100.0 * (v.ca - v.cout_marchandises) / v.ca, 1)       AS marge_brute_pct,
       ROUND(s.masse_salariale, 0)                                 AS masse_salariale,
       ROUND(f.charges, 0)                                         AS charges,
       ROUND(p.marketing, 0)                                       AS marketing,
       ROUND(v.ca - v.cout_marchandises - s.masse_salariale - f.charges - p.marketing, 0)
                                                                   AS resultat_exploitation,
       ROUND(100.0 * (v.ca - v.cout_marchandises - s.masse_salariale - f.charges - p.marketing)
             / v.ca, 1)                                            AS resultat_pct
FROM ventes v
JOIN salaires s ON s.annee = v.annee
JOIN frais    f ON f.annee = v.annee
JOIN pub      p ON p.annee = v.annee
ORDER BY v.annee;


-- @marge_par_famille
-- Où la marge se dégrade-t-elle ? Comparaison des deux exercices, famille par famille.
SELECT p.famille,
       ROUND(SUM(CASE WHEN d.annee = 2024 THEN v.montant_ht END), 0)          AS ca_2024,
       ROUND(SUM(CASE WHEN d.annee = 2025 THEN v.montant_ht END), 0)          AS ca_2025,
       ROUND(100.0 * SUM(CASE WHEN d.annee = 2024 THEN v.marge END)
             / SUM(CASE WHEN d.annee = 2024 THEN v.montant_ht END), 1)        AS marge_2024_pct,
       ROUND(100.0 * SUM(CASE WHEN d.annee = 2025 THEN v.marge END)
             / SUM(CASE WHEN d.annee = 2025 THEN v.montant_ht END), 1)        AS marge_2025_pct,
       ROUND(100.0 * SUM(CASE WHEN d.annee = 2025 THEN v.marge END)
             / SUM(CASE WHEN d.annee = 2025 THEN v.montant_ht END)
           - 100.0 * SUM(CASE WHEN d.annee = 2024 THEN v.marge END)
             / SUM(CASE WHEN d.annee = 2024 THEN v.montant_ht END), 1)        AS variation_points
FROM fait_ventes v
JOIN dim_date d    ON d.date_id = v.date_commande_id
JOIN dim_produit p ON p.produit_id = v.produit_id
GROUP BY p.famille
ORDER BY variation_points;


-- @cout_achat_par_fournisseur
-- La dégradation de marge vient-elle des prix de vente ou des coûts d'achat ?
-- Coût unitaire moyen payé à chaque fournisseur, avant et après.
-- La jointure ventes -> produit -> fournisseur est exactement ce que le schéma en
-- étoile rend possible : aucune des trois sources ne contient à elle seule ce lien.
SELECT f.nom AS fournisseur,
       COUNT(DISTINCT p.sku)                                                  AS nb_articles,
       ROUND(SUM(CASE WHEN d.annee = 2024 THEN v.montant_ht END), 0)          AS ca_2024,
       ROUND(SUM(CASE WHEN d.annee = 2025 THEN v.montant_ht END), 0)          AS ca_2025,
       ROUND(SUM(CASE WHEN d.annee = 2024 THEN v.cout_total END)
             / SUM(CASE WHEN d.annee = 2024 THEN v.quantite END), 2)          AS cout_unitaire_2024,
       ROUND(SUM(CASE WHEN d.annee = 2025 THEN v.cout_total END)
             / SUM(CASE WHEN d.annee = 2025 THEN v.quantite END), 2)          AS cout_unitaire_2025,
       ROUND(100.0 * (SUM(CASE WHEN d.annee = 2025 THEN v.cout_total END)
                      / SUM(CASE WHEN d.annee = 2025 THEN v.quantite END))
             / (SUM(CASE WHEN d.annee = 2024 THEN v.cout_total END)
                / SUM(CASE WHEN d.annee = 2024 THEN v.quantite END)) - 100, 1) AS variation_cout_pct,
       ROUND(SUM(CASE WHEN d.annee = 2025 THEN v.marge END), 0)               AS marge_2025
FROM fait_ventes v
JOIN dim_date d        ON d.date_id = v.date_commande_id
JOIN dim_produit p     ON p.produit_id = v.produit_id
JOIN dim_fournisseur f ON f.code = p.fournisseur_code
GROUP BY f.nom
HAVING ca_2024 IS NOT NULL AND ca_2025 IS NOT NULL
ORDER BY variation_cout_pct DESC
LIMIT 8;


-- @impact_chiffre_derive
-- Chiffrage de l'impact : marge qu'aurait dégagée 2025 si le coût unitaire moyen
-- du fournisseur en cause était resté au niveau de 2024, à volumes et prix identiques.
WITH cout_2024 AS (
    SELECT v.produit_id,
           SUM(v.cout_total) / SUM(v.quantite) AS cout_unitaire_ref
    FROM fait_ventes v
    JOIN dim_date d ON d.date_id = v.date_commande_id
    WHERE d.annee = 2024
    GROUP BY v.produit_id
)
SELECT f.nom                                                        AS fournisseur,
       ROUND(SUM(v.montant_ht), 0)                                  AS ca_2025,
       ROUND(SUM(v.marge), 0)                                       AS marge_reelle_2025,
       ROUND(SUM(v.montant_ht - v.quantite * c.cout_unitaire_ref), 0) AS marge_a_cout_2024,
       ROUND(SUM(v.montant_ht - v.quantite * c.cout_unitaire_ref) - SUM(v.marge), 0)
                                                                    AS manque_a_gagner
FROM fait_ventes v
JOIN dim_date d        ON d.date_id = v.date_commande_id
JOIN dim_produit p     ON p.produit_id = v.produit_id
JOIN dim_fournisseur f ON f.code = p.fournisseur_code
JOIN cout_2024 c       ON c.produit_id = v.produit_id
WHERE d.annee = 2025
GROUP BY f.nom
ORDER BY manque_a_gagner DESC
LIMIT 5;


-- @concentration_clients
-- Risque de dépendance commerciale : quelle part du chiffre d'affaires repose sur
-- les plus gros comptes ?
WITH par_client AS (
    SELECT c.nom, c.segment, SUM(v.montant_ht) AS ca
    FROM fait_ventes v
    JOIN dim_client c ON c.client_id = v.client_id
    GROUP BY c.client_id
),
classe AS (
    SELECT nom, segment, ca,
           ROW_NUMBER() OVER (ORDER BY ca DESC) AS rang,
           SUM(ca) OVER () AS ca_total
    FROM par_client
)
SELECT rang, nom, segment, ROUND(ca, 0) AS ca,
       ROUND(100.0 * ca / ca_total, 2)                                        AS part_pct,
       ROUND(100.0 * SUM(ca) OVER (ORDER BY ca DESC) / ca_total, 1)           AS part_cumulee_pct
FROM classe
WHERE rang <= 10
ORDER BY rang;


-- @rotation_stock
-- Rotation des stocks par entrepôt = coût des marchandises vendues / stock moyen.
-- Le stock est un fait de type « photo » : on en prend la MOYENNE sur l'année,
-- jamais la somme (sommer 12 photos mensuelles n'a aucun sens physique).
WITH cout_vendu AS (
    SELECT v.entrepot_id, d.annee, SUM(v.cout_total) AS cmv
    FROM fait_ventes v JOIN dim_date d ON d.date_id = v.date_commande_id
    GROUP BY v.entrepot_id, d.annee
),
stock_mensuel AS (
    SELECT s.entrepot_id, d.annee, d.mois_annee, SUM(s.valeur_stock) AS valeur
    FROM fait_stock s JOIN dim_date d ON d.date_id = s.date_id
    GROUP BY s.entrepot_id, d.annee, d.mois_annee
),
stock_moyen AS (
    SELECT entrepot_id, annee, AVG(valeur) AS valeur_moyenne
    FROM stock_mensuel GROUP BY entrepot_id, annee
)
SELECT e.nom AS entrepot, c.annee,
       ROUND(c.cmv, 0)                        AS cout_marchandises_vendues,
       ROUND(s.valeur_moyenne, 0)             AS stock_moyen,
       ROUND(c.cmv / s.valeur_moyenne, 2)     AS rotation,
       ROUND(365.0 / (c.cmv / s.valeur_moyenne), 0) AS jours_de_stock
FROM cout_vendu c
JOIN stock_moyen s  ON s.entrepot_id = c.entrepot_id AND s.annee = c.annee
JOIN dim_entrepot e ON e.entrepot_id = c.entrepot_id
ORDER BY c.annee, rotation;


-- @delai_paiement
-- Délai moyen d'encaissement (DSO) et encours client non réglé.
SELECT d.annee,
       COUNT(*)                                                     AS lignes_facturees,
       ROUND(AVG(v.delai_paiement_jours), 1)                        AS dso_moyen_jours,
       SUM(CASE WHEN v.date_paiement_id IS NULL THEN 1 ELSE 0 END)  AS lignes_non_reglees,
       ROUND(SUM(CASE WHEN v.date_paiement_id IS NULL THEN v.montant_ht ELSE 0 END), 0)
                                                                    AS encours_non_regle
FROM fait_ventes v
JOIN dim_date d ON d.date_id = v.date_commande_id
GROUP BY d.annee;


-- @performance_marketing
-- Coût par prospect et coût par nouveau client, canal par canal.
-- Attention : le rattachement d'un nouveau client à un canal provient du suivi
-- manuel des campagnes, pas d'un modèle d'attribution. C'est une donnée déclarative.
SELECT c.canal,
       ROUND(SUM(m.depense), 0)                          AS depense_totale,
       SUM(m.prospects)                                  AS prospects,
       SUM(m.nouveaux_clients)                           AS nouveaux_clients,
       ROUND(SUM(m.depense) / NULLIF(SUM(m.prospects), 0), 2)        AS cout_par_prospect,
       ROUND(SUM(m.depense) / NULLIF(SUM(m.nouveaux_clients), 0), 0) AS cout_par_client
FROM fait_marketing m
JOIN dim_canal_marketing c ON c.canal_id = m.canal_id
GROUP BY c.canal
ORDER BY cout_par_client;


-- @masse_salariale
-- La masse salariale suit-elle la croissance du chiffre d'affaires ?
WITH ca AS (
    SELECT d.annee, SUM(v.montant_ht) AS ca
    FROM fait_ventes v JOIN dim_date d ON d.date_id = v.date_commande_id
    GROUP BY d.annee
),
paie AS (
    SELECT d.annee, SUM(p.cout_total) AS masse,
           COUNT(DISTINCT p.employe_id) AS effectif_paye
    FROM fait_paie p JOIN dim_date d ON d.date_id = p.date_id
    GROUP BY d.annee
)
SELECT ca.annee, ROUND(ca.ca, 0) AS ca, ROUND(p.masse, 0) AS masse_salariale,
       p.effectif_paye,
       ROUND(100.0 * p.masse / ca.ca, 1)   AS masse_sur_ca_pct,
       ROUND(ca.ca / p.effectif_paye, 0)   AS ca_par_employe
FROM ca JOIN paie p ON p.annee = ca.annee
ORDER BY ca.annee;


-- @roulement_personnel
-- Taux de roulement par département : départs rapportés à l'effectif du département.
SELECT departement,
       COUNT(*)                                                  AS effectif_total,
       SUM(CASE WHEN est_actif = 0 THEN 1 ELSE 0 END)            AS departs,
       ROUND(100.0 * SUM(CASE WHEN est_actif = 0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                 AS taux_roulement_pct
FROM dim_employe
GROUP BY departement
ORDER BY taux_roulement_pct DESC;


-- @ponctualite_fournisseurs
-- Fiabilité de livraison : part des réceptions en retard et retard moyen.
SELECT f.nom AS fournisseur, f.pays,
       COUNT(*)                                                          AS receptions,
       SUM(CASE WHEN a.retard_jours > 0 THEN 1 ELSE 0 END)               AS en_retard,
       ROUND(100.0 * SUM(CASE WHEN a.retard_jours > 0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                         AS taux_retard_pct,
       ROUND(AVG(CASE WHEN a.retard_jours > 0 THEN a.retard_jours END), 1) AS retard_moyen_jours
FROM fait_achats a
JOIN dim_fournisseur f ON f.fournisseur_id = a.fournisseur_id
WHERE a.retard_jours IS NOT NULL
GROUP BY f.nom, f.pays
HAVING receptions >= 20
ORDER BY taux_retard_pct DESC
LIMIT 8;


-- @saisonnalite
-- Profil mensuel du chiffre d'affaires : un grossiste vend avant la saison de détail.
SELECT d.mois, d.nom_mois,
       ROUND(SUM(CASE WHEN d.annee = 2024 THEN v.montant_ht END), 0) AS ca_2024,
       ROUND(SUM(CASE WHEN d.annee = 2025 THEN v.montant_ht END), 0) AS ca_2025
FROM fait_ventes v
JOIN dim_date d ON d.date_id = v.date_commande_id
GROUP BY d.mois, d.nom_mois
ORDER BY d.mois;


-- @qualite_donnees
-- Synthèse du journal de nettoyage, par nature de défaut.
SELECT motif,
       SUM(CASE WHEN action = 'rejetee' THEN 1 ELSE 0 END)  AS lignes_rejetees,
       SUM(CASE WHEN action <> 'rejetee' THEN 1 ELSE 0 END) AS valeurs_traitees,
       COUNT(*)                                             AS total
FROM qualite_rejets
GROUP BY motif
ORDER BY total DESC;
