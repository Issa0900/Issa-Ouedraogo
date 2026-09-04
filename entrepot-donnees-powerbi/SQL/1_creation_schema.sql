-- =============================================================================
-- Boréal Distribution inc. — entrepôt de données décisionnel
-- Schéma en étoile : 7 dimensions, 6 tables de faits, 1 table de qualité.
--
-- Conçu pour être consommé par Power BI :
--   - clés de substitution entières (jointures rapides, indépendantes des codes métier) ;
--   - une seule table de dates partagée par tous les faits (une « table de dates »
--     unique est la condition pour que la time intelligence DAX fonctionne) ;
--   - les mesures ne sont PAS pré-agrégées ici : le grain reste la ligne de commande,
--     Power BI agrège. Pré-agréger interdirait tout forage.
--
-- Cible : SQLite (fichier data/entrepot/boreal.db). La syntaxe reste volontairement
-- proche du SQL standard pour rester portable vers PostgreSQL ou SQL Server.
-- =============================================================================

DROP TABLE IF EXISTS fait_ventes;
DROP TABLE IF EXISTS fait_achats;
DROP TABLE IF EXISTS fait_stock;
DROP TABLE IF EXISTS fait_paie;
DROP TABLE IF EXISTS fait_marketing;
DROP TABLE IF EXISTS fait_charges;
DROP TABLE IF EXISTS qualite_rejets;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_client;
DROP TABLE IF EXISTS dim_produit;
DROP TABLE IF EXISTS dim_fournisseur;
DROP TABLE IF EXISTS dim_employe;
DROP TABLE IF EXISTS dim_entrepot;
DROP TABLE IF EXISTS dim_canal_marketing;

-- -----------------------------------------------------------------------------
-- Dimensions
-- -----------------------------------------------------------------------------

-- Calendrier continu : aucune date ne doit manquer, sinon les cumuls annuels
-- glissants de Power BI trouent silencieusement.
CREATE TABLE dim_date (
    date_id       INTEGER PRIMARY KEY,   -- AAAAMMJJ
    date          TEXT    NOT NULL,
    annee         INTEGER NOT NULL,
    trimestre     TEXT    NOT NULL,
    mois          INTEGER NOT NULL,
    nom_mois      TEXT    NOT NULL,
    mois_annee    TEXT    NOT NULL,      -- 'AAAA-MM', pratique pour trier un axe mensuel
    semaine       INTEGER NOT NULL,
    jour_semaine  INTEGER NOT NULL,
    nom_jour      TEXT    NOT NULL,
    est_weekend   INTEGER NOT NULL
);

CREATE TABLE dim_client (
    client_id           INTEGER PRIMARY KEY,
    code                TEXT NOT NULL UNIQUE,
    nom                 TEXT NOT NULL,
    type_commerce       TEXT,
    ville               TEXT,
    province            TEXT,
    code_postal         TEXT,
    segment             TEXT,             -- A / B / C selon le volume d'achat
    conditions_paiement TEXT,
    courriel            TEXT,
    date_ouverture      TEXT,
    fiches_fusionnees   INTEGER NOT NULL  -- >1 : plusieurs fiches CRM rapprochées ici
);

CREATE TABLE dim_produit (
    produit_id       INTEGER PRIMARY KEY,
    sku              TEXT NOT NULL UNIQUE,
    designation      TEXT NOT NULL,
    famille          TEXT NOT NULL,
    fournisseur_code TEXT,
    cout_standard    REAL,                -- NULL si absent du catalogue (signalé, pas inventé)
    prix_liste       REAL,
    poids_kg         REAL
);

CREATE TABLE dim_fournisseur (
    fournisseur_id    INTEGER PRIMARY KEY,
    code              TEXT NOT NULL UNIQUE,
    nom               TEXT NOT NULL,
    pays              TEXT,
    delai_moyen_jours INTEGER,
    conditions        TEXT
);

CREATE TABLE dim_employe (
    employe_id     INTEGER PRIMARY KEY,
    matricule      TEXT NOT NULL UNIQUE,
    prenom         TEXT,
    nom            TEXT,
    nom_complet    TEXT,
    poste          TEXT,
    departement    TEXT,
    entrepot_code  TEXT,
    date_embauche  TEXT,
    date_depart    TEXT,
    salaire_annuel REAL,
    statut         TEXT,
    est_actif      INTEGER NOT NULL
);

CREATE TABLE dim_entrepot (
    entrepot_id INTEGER PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    nom         TEXT NOT NULL,
    region      TEXT,
    surface_m2  INTEGER
);

CREATE TABLE dim_canal_marketing (
    canal_id INTEGER PRIMARY KEY,
    canal    TEXT NOT NULL UNIQUE
);

-- -----------------------------------------------------------------------------
-- Faits
-- -----------------------------------------------------------------------------

-- Grain : une ligne d'article dans une commande client.
-- montant_ht, cout_total et marge sont calculés à l'ETL parce qu'ils dépendent du
-- prix et du coût *au moment de la vente* — les recalculer plus tard à partir du
-- catalogue courant réécrirait l'histoire à chaque évolution de tarif.
CREATE TABLE fait_ventes (
    vente_id              INTEGER PRIMARY KEY,
    no_commande           TEXT NOT NULL,
    date_commande_id      INTEGER NOT NULL REFERENCES dim_date(date_id),
    date_livraison_id     INTEGER REFERENCES dim_date(date_id),
    date_paiement_id      INTEGER REFERENCES dim_date(date_id),   -- NULL = facture ouverte
    client_id             INTEGER NOT NULL REFERENCES dim_client(client_id),
    produit_id            INTEGER NOT NULL REFERENCES dim_produit(produit_id),
    entrepot_id           INTEGER NOT NULL REFERENCES dim_entrepot(entrepot_id),
    employe_id            INTEGER REFERENCES dim_employe(employe_id),
    quantite              INTEGER NOT NULL,
    prix_unitaire         REAL NOT NULL,
    remise_pct            REAL,
    cout_unitaire         REAL NOT NULL,
    montant_ht            REAL NOT NULL,
    cout_total            REAL NOT NULL,
    marge                 REAL NOT NULL,
    canal_vente           TEXT,
    delai_paiement_jours  INTEGER,
    delai_livraison_jours INTEGER
);

-- Grain : une ligne d'article dans une commande fournisseur.
CREATE TABLE fait_achats (
    achat_id         INTEGER PRIMARY KEY,
    no_achat         TEXT NOT NULL,
    date_commande_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    date_prevue_id   INTEGER REFERENCES dim_date(date_id),
    date_reception_id INTEGER REFERENCES dim_date(date_id),
    fournisseur_id   INTEGER NOT NULL REFERENCES dim_fournisseur(fournisseur_id),
    produit_id       INTEGER NOT NULL REFERENCES dim_produit(produit_id),
    quantite         INTEGER NOT NULL,     -- négative = retour au fournisseur
    cout_unitaire    REAL NOT NULL,
    montant          REAL NOT NULL,
    statut           TEXT,
    est_retour       INTEGER NOT NULL,
    retard_jours     INTEGER               -- réception réelle - réception prévue
);

-- Grain : photo mensuelle d'un article dans un entrepôt (fait de type « snapshot »).
-- À ne jamais sommer sur l'axe du temps — seule la moyenne ou la dernière valeur
-- ont un sens. Le guide DAX le rappelle explicitement.
CREATE TABLE fait_stock (
    stock_id       INTEGER PRIMARY KEY,
    date_id        INTEGER NOT NULL REFERENCES dim_date(date_id),
    entrepot_id    INTEGER NOT NULL REFERENCES dim_entrepot(entrepot_id),
    produit_id     INTEGER NOT NULL REFERENCES dim_produit(produit_id),
    quantite       INTEGER NOT NULL,
    cout_unitaire  REAL NOT NULL,
    valeur_stock   REAL NOT NULL,
    seuil_minimum  INTEGER,
    sous_seuil     INTEGER NOT NULL
);

-- Grain : un employé, un mois.
CREATE TABLE fait_paie (
    paie_id                INTEGER PRIMARY KEY,
    date_id                INTEGER NOT NULL REFERENCES dim_date(date_id),
    employe_id             INTEGER NOT NULL REFERENCES dim_employe(employe_id),
    salaire_base           REAL,
    primes                 REAL,
    heures_supplementaires REAL,
    charges_sociales       REAL,
    cout_total             REAL NOT NULL
);

-- Grain : un canal, un mois.
CREATE TABLE fait_marketing (
    marketing_id     INTEGER PRIMARY KEY,
    date_id          INTEGER NOT NULL REFERENCES dim_date(date_id),
    canal_id         INTEGER NOT NULL REFERENCES dim_canal_marketing(canal_id),
    budget           REAL,
    depense          REAL NOT NULL,
    prospects        INTEGER,
    nouveaux_clients INTEGER,
    ecart_budget     REAL
);

-- Grain : une catégorie de charge, un entrepôt, un mois.
CREATE TABLE fait_charges (
    charge_id   INTEGER PRIMARY KEY,
    date_id     INTEGER NOT NULL REFERENCES dim_date(date_id),
    categorie   TEXT NOT NULL,
    entrepot_id INTEGER NOT NULL REFERENCES dim_entrepot(entrepot_id),
    montant     REAL NOT NULL
);

-- -----------------------------------------------------------------------------
-- Traçabilité qualité
-- -----------------------------------------------------------------------------
-- Chaque ligne écartée ou corrigée par l'ETL laisse une trace ici, avec sa valeur
-- d'origine. C'est ce qui permet d'afficher dans Power BI une page « qualité des
-- données » vérifiable, plutôt qu'un nombre de lignes chargées sans contexte.
CREATE TABLE qualite_rejets (
    rejet_id INTEGER PRIMARY KEY,
    source   TEXT NOT NULL,   -- fichier d'origine
    cle      TEXT,            -- identifiant métier de la ligne concernée
    champ    TEXT,            -- colonne en cause
    valeur   TEXT,            -- valeur brute rencontrée
    motif    TEXT NOT NULL,   -- date_illisible, article_inconnu, doublon_exact, ...
    action   TEXT NOT NULL    -- rejetee / corrigee / signalee / conservee comme retour
);

-- -----------------------------------------------------------------------------
-- Index : les axes de filtrage réellement utilisés par le rapport.
-- -----------------------------------------------------------------------------
CREATE INDEX ix_ventes_date     ON fait_ventes (date_commande_id);
CREATE INDEX ix_ventes_client   ON fait_ventes (client_id);
CREATE INDEX ix_ventes_produit  ON fait_ventes (produit_id);
CREATE INDEX ix_ventes_entrepot ON fait_ventes (entrepot_id);
CREATE INDEX ix_achats_date     ON fait_achats (date_commande_id);
CREATE INDEX ix_achats_frn      ON fait_achats (fournisseur_id);
CREATE INDEX ix_stock_date      ON fait_stock  (date_id, entrepot_id);
CREATE INDEX ix_paie_date       ON fait_paie   (date_id);
CREATE INDEX ix_charges_date    ON fait_charges(date_id);
CREATE INDEX ix_rejets_motif    ON qualite_rejets (motif, action);
