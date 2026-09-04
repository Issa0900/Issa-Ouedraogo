# Rapport de qualite des donnees — Boreal Distribution

_Genere automatiquement par `Python/3_controle_qualite.py`. Ne pas editer a la main._


**642 lignes rejetees** et **1181 valeurs corrigees ou signalees** sur l'ensemble des 8 sources.


## 1. Reconciliation : anomalies injectees vs anomalies detectees

Le generateur de donnees journalise chaque anomalie qu'il injecte. L'ETL journalise chaque anomalie qu'il rencontre. Les deux journaux sont produits independamment : leur confrontation mesure ce que le nettoyage laisse reellement passer.


| Motif | Injecte | Detecte | Ecart | Regle appliquee |
|---|---:|---:|---:|---|
| `date_illisible` | 92 | 92 | 0 | Dates inexploitables ('31/02/2024', '00/00/0000', vide) : la ligne est ecartee, aucune date n'est devinee. |
| `article_inconnu` | 135 | 135 | 0 | Reference article absente du catalogue : la ligne ne peut etre rattachee ni a une famille ni a un fournisseur. |
| `quantite_invalide` | 76 | 76 | 0 | Quantite nulle ou negative sur une vente, ou comptage d'inventaire negatif. |
| `prix_invalide` | 31 | 31 | 0 | Prix de vente a zero. |
| `prix_aberrant` | 26 | 26 | 0 | Prix superieur a 3x le prix de liste : virgule oubliee a la saisie. |
| `doublon_exact` | 277 | 277 | 0 | Ligne strictement identique a une ligne deja chargee (double import, script d'extraction relance). |
| `doublon_metier` | 14 | 14 | 0 | Meme entreprise saisie sous deux codes clients : les fiches sont fusionnees et les ventes rattachees au code conserve. |
| `ligne_technique` | 5 | 5 | 0 | Ligne de total ou pied de page ajoute par l'outil d'export. |
| `valeur_manquante` | 162 | 162 | 0 | Champ non renseigne : conserve a NULL ou libelle 'Non renseigne', jamais impute. |
| `casse_ou_espaces` | 370 | 370 | 0 | Espaces parasites ou casse incoherente sur une cle ou un libelle. |
| `variante_ecriture` | 552 | 552 | 0 | Meme valeur ecrite de plusieurs facons ('QC' / 'Quebec' / 'Québec') : ramenee a une forme unique. |
| `courriel_invalide` | 9 | 9 | 0 | Courriel non conforme ('achats@', 'n/a') : mis a NULL plutot que conserve tel quel. |
| `nombre_en_texte` | 32 | 31 | -1 | Montant saisi en texte ('52 000 $') dans le classeur RH. |
| `cout_standard_absent` | 5 | 5 | 0 | Cout standard a zero au catalogue : la fiche est conservee, le defaut est signale. |
| `quantite_negative` | 38 | 38 | 0 | Quantite negative sur un achat : ce n'est pas une erreur mais un retour fournisseur, conserve et qualifie. |
| **Total** | **1824** | **1823** | | |

### Ecarts expliques

- **`nombre_en_texte`** — Un salaire en texte figurait sur la ligne d'un employe en double, ecartee plus tot comme doublon exact : le defaut de format n'a donc jamais eu a etre corrige.

### Verdict

Aucun ecart inexplique : chaque anomalie injectee a ete retrouvee et traitee par l'ETL, ou son absence est justifiee ci-dessus.

## 2. Volumetrie par source

| Source | Format | Lignes lues | Lignes chargees | Taux de retenue |
|---|---|---:|---:|---:|
| ERP ventes (2 fichiers) | CSV ';' cp1252 | 16 127 | 15 683 | 97,2 % |
| Achats fournisseurs | CSV tabulation UTF-8 | 2 122 | 2 097 | 98,8 % |
| Inventaire | CSV ',' UTF-8 | 10 480 | 10 335 | 98,6 % |
| Charges comptables | CSV ';' latin-1 | 569 | 552 | 97,0 % |
| Catalogue produits | CSV ',' UTF-8 | 190 | 182 | 95,8 % |
| CRM clients | JSON imbrique UTF-8 | 234 | 220 | 94,0 % |
| Marketing | JSON UTF-8 | 84 | 84 | 100,0 % |
| RH employes | XLSX 2 feuilles | 50 | 47 | 94,0 % |
| RH paie | XLSX 2 feuilles | 1 002 | 1 002 | 100,0 % |

## 3. Completude des champs cles apres chargement

Aucune valeur n'a ete imputee : un champ absent reste absent. Ces taux mesurent donc ce que les systemes sources fournissent reellement.


| Table | Champ | Renseigne | Total | Taux |
|---|---|---:|---:|---:|
| `dim_client` | code_postal | 207 | 220 | 94,1 % |
| `dim_client` | courriel | 201 | 220 | 91,4 % |
| `dim_client` | province | 220 | 220 | 100,0 % |
| `dim_produit` | cout_standard | 177 | 182 | 97,3 % |
| `fait_ventes` | date_paiement_id | 14 104 | 15 683 | 89,9 % |
| `fait_ventes` | canal renseigne | 15 549 | 15 683 | 99,1 % |

## 4. Principe de traitement

| Situation | Decision | Pourquoi |
|---|---|---|
| Format reparable (date, montant, casse, espace insecable) | **Corrigee**, ligne conservee | Le defaut est de forme, l'information metier est intacte. |
| Variante d'ecriture d'une meme valeur | **Normalisee** via table de correspondance | Une regle de casse automatique casserait `Logiciels et TI`. |
| Valeur absente | **Conservee a NULL** | Imputer une moyenne fabriquerait une donnee qui n'existe pas. |
| Cle metier introuvable (article, client) | **Rejetee**, tracee | Rattacher a un « divers » fausserait toutes les analyses par famille. |
| Ligne strictement identique | **Rejetee**, tracee | Double import : la conserver doublerait le chiffre d'affaires. |
| Deux fiches pour la meme entreprise | **Fusionnees**, ventes rattachees | Sinon le CA d'un client est eclate et la concentration sous-estimee. |
| Quantite negative sur un achat | **Conservee**, qualifiee de retour | Ce n'est pas une erreur : c'est une operation reelle. |
