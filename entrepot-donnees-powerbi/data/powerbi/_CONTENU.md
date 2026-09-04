# Contenu de l'export Power BI

_Genere par `Python/5_exporter_powerbi.py`. Encodage UTF-8 avec BOM, separateur `,`, decimale `.`, dates ISO._

| Fichier | Lignes | Colonnes | Taille | Grain |
|---|---:|---:|---:|---|
| `dim_date.csv` | 912 | 11 | 54 Ko | 1 ligne par jour (2024-01-01 au 2026-06-30) |
| `dim_client.csv` | 220 | 12 | 28 Ko | 1 ligne par client  apres fusion des fiches en double |
| `dim_produit.csv` | 182 | 8 | 14 Ko | 1 ligne par article du catalogue |
| `dim_fournisseur.csv` | 22 | 6 | 1 Ko | 1 ligne par fournisseur |
| `dim_employe.csv` | 47 | 13 | 6 Ko | 1 ligne par employe |
| `dim_entrepot.csv` | 3 | 5 | 0 Ko | 1 ligne par entrepot |
| `dim_canal_marketing.csv` | 5 | 2 | 0 Ko | 1 ligne par canal |
| `fait_ventes.csv` | 15 683 | 19 | 1 750 Ko | 1 ligne par article dans une commande client |
| `fait_achats.csv` | 2 097 | 13 | 157 Ko | 1 ligne par article dans une commande fournisseur |
| `fait_stock.csv` | 10 335 | 9 | 425 Ko | 1 photo mensuelle par article et par entrepot (NE PAS SOMMER dans le temps) |
| `fait_paie.csv` | 1 002 | 8 | 48 Ko | 1 ligne par employe et par mois |
| `fait_marketing.csv` | 84 | 8 | 4 Ko | 1 ligne par canal et par mois |
| `fait_charges.csv` | 552 | 5 | 22 Ko | 1 ligne par categorie de charge  entrepot et mois |
| `qualite_rejets.csv` | 1 823 | 7 | 154 Ko | 1 ligne par anomalie rencontree par l'ETL |
