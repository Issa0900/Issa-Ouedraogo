-- Geomarketing Québec — schéma de base
-- Compatible SQLite / PostgreSQL (types génériques, pas d'extensions propriétaires)

CREATE TABLE regions (
    region_id       INTEGER PRIMARY KEY,
    nom_region      TEXT NOT NULL UNIQUE,      -- ex. "Chaudière-Appalaches"
    code_region_isq TEXT                        -- code région administrative ISQ (01 à 17)
);

CREATE TABLE population (
    region_id           INTEGER NOT NULL REFERENCES regions(region_id),
    annee                INTEGER NOT NULL,
    population_totale    INTEGER NOT NULL,
    age_moyen            NUMERIC(4,1),
    part_0_19            NUMERIC(5,2),          -- % de la population 0-19 ans
    part_20_64           NUMERIC(5,2),
    part_65_plus         NUMERIC(5,2),
    PRIMARY KEY (region_id, annee)
);

CREATE TABLE revenus (
    region_id                INTEGER NOT NULL REFERENCES regions(region_id),
    annee                     INTEGER NOT NULL,
    revenu_disponible_habitant NUMERIC(10,2) NOT NULL,  -- $ par habitant
    PRIMARY KEY (region_id, annee)
);

CREATE TABLE entreprises (
    entreprise_id     INTEGER PRIMARY KEY,
    region_id         INTEGER NOT NULL REFERENCES regions(region_id),
    nom_entreprise    TEXT,
    secteur_activite  TEXT,                    -- code SCIAN, voir guide du Registraire
    date_immatriculation DATE
);

-- Table clients : optionnelle, à remplir avec les données CRM propres à la PME si
-- disponibles (non fournie par les sources publiques). Sert à valider le profil client
-- réel contre le profil client théorique par région (analyse 4).
CREATE TABLE clients (
    client_id     INTEGER PRIMARY KEY,
    region_id     INTEGER REFERENCES regions(region_id),
    age           INTEGER,
    revenu_estime NUMERIC(10,2)
);

-- Vue de synthèse par région (dernière année disponible) pour alimenter les analyses
-- 1 à 5 du rapport (taille de marché, croissance, concurrence, score d'opportunité).
CREATE VIEW v_synthese_region AS
SELECT
    r.region_id,
    r.nom_region,
    p.annee,
    p.population_totale,
    p.age_moyen,
    rv.revenu_disponible_habitant,
    COUNT(e.entreprise_id)                                        AS nb_entreprises,
    COUNT(e.entreprise_id) * 1.0 / NULLIF(p.population_totale, 0) AS indice_concurrence,
    p.population_totale * rv.revenu_disponible_habitant           AS potentiel_marche
FROM regions r
JOIN population p ON p.region_id = r.region_id
JOIN revenus rv   ON rv.region_id = r.region_id AND rv.annee = p.annee
LEFT JOIN entreprises e ON e.region_id = r.region_id
GROUP BY r.region_id, r.nom_region, p.annee, p.population_totale, p.age_moyen,
         rv.revenu_disponible_habitant;
