# Sources de données — Geomarketing Québec

Sources réelles, vérifiées le 2026-08-04. Méthode finalement retenue : scriptée de bout en
bout (voir `Python/1_telecharger_entreprises.py` à `5_analyse_marche.py`), sans export manuel.

## 1. Population, croissance, revenu disponible, chômage — ISQ

Les tableaux dynamiques habituels de l'ISQ (BDSO — Banque de données des statistiques
officielles) n'exposent ni lien CSV ni API publique exploitable par script : le tableau se
charge côté client via une application Next.js minifiée, sans endpoint devinable. Piste
initialement envisagée (export manuel via le bouton "Exporter vers Excel") :
- Population totale : https://statistique.quebec.ca/fr/produit/tableau/estimations-population-regions-administratives
- Âge moyen/médian : https://statistique.quebec.ca/fr/produit/tableau/population-age-sex-median-administrative-regions-quebec
- Revenu disponible par habitant : https://statistique.quebec.ca/fr/produit/tableau/per-capita-disposable-income-administrative-regions-all-of-quebec

**Méthode retenue à la place** : les 17 fiches "Coup d'œil sur les régions" de l'ISQ
(`https://statistique.quebec.ca/fr/produit/publication/<slug>-panorama`, ex.
`chaudiere-appalaches-panorama`) intègrent, dans le JSON `__NEXT_DATA__` de la page (champ
`props.pageProps.data.html`), plusieurs éditions (2022 à 2024) d'indicateurs clés en texte :
population totale, taux de croissance annuel, revenu disponible par habitant, taux de
chômage, PIB, principaux secteurs économiques. C'est du texte serveur-rendu, donc lisible
par simple requête HTTP — pas besoin de navigateur. Liste des 17 slugs dans
`Python/2_scraper_isq_regions.py`.

Limite : chaque indicateur garde l'année de la dernière édition où il apparaît (l'ISQ ne
republie pas tous les indicateurs à chaque édition — ex. revenu disponible absent de
l'édition 2024, présent dans l'édition 2023 avec des données 2021). D'où les colonnes
`annee_population`, `annee_revenu`, `annee_chomage` distinctes dans `isq_regions.csv`.

Vérification de cohérence : somme des populations extraites des 17 régions = 8 874 683,
à comparer aux ~8,87 M d'habitants publiés par l'ISQ pour le Québec au 1er juillet 2023 — 
concordance quasi parfaite, confirme la fiabilité de l'extraction.

Page complémentaire utile pour une mise à jour manuelle future : https://statistique.quebec.ca/fr/vitrine/region

## 2. Registre des entreprises du Québec — Registraire des entreprises (données ouvertes)

- Page catalogue : https://www.donneesquebec.ca/recherche/dataset/registre-des-entreprises
- **Téléchargement direct (ZIP, ~255 Mo)** :
  https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/GR03A2_22A_PIU_RecupDonnPub_PC/FichierDonneesOuvertes.aspx
- Guide d'utilisation (structure des fichiers, codes de secteur d'activité) :
  https://www.donneesquebec.ca/recherche/dataset/6f710997-b5f9-4347-893b-1a47ddb61437/resource/09008d3a-2e0e-4613-ab43-bd833f381929/download/guideutilisation.pdf
- Licence : CC-BY-NC-SA 4.0 (attribution, usage non commercial, partage dans les mêmes
  conditions) → mentionner la source si republié, ne pas revendre les données.
- Mise à jour : régénéré mensuellement.
- Contenu utilisé : `Etablissements.csv` (257 755 lignes) — adresse municipale de chaque
  établissement. Le registre ne donne pas de code de région administrative directement : la
  ville est rattachée à sa région via `Python/ville_region.py` (dictionnaire des ~500
  municipalités les plus fréquentes), couvrant ~81% des établissements. Le reste ("non
  classé") est exclu du calcul de l'indice de concurrence.
- URL stable → téléchargée par script (`Python/1_telecharger_entreprises.py`).

## Pipeline complet

```
1_telecharger_entreprises.py       → data/entreprises_raw.zip
2_scraper_isq_regions.py            → data/raw_isq/*.html
3_extraire_indicateurs_isq.py       → data/isq_regions.csv
4_compter_entreprises_par_region.py → data/entreprises_regions.csv
5_analyse_marche.py                 → data/synthese_regions.csv + Rapport/score_opportunite.png
```
