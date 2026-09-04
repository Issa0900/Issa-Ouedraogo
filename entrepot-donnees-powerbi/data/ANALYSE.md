# Resultats d'analyse — Boreal Distribution

_Genere automatiquement par `Python/4_analyser.py` a partir de `SQL/2_requetes_analyse.sql`. Ne pas editer a la main._


## Compte de resultat simplifie

<sub>Requete `@resultat_par_annee` — `SQL/2_requetes_analyse.sql`</sub>


| annee | ca | nb commandes | panier moyen | marge brute | marge brute pct | masse salariale | charges | marketing | resultat exploitation | resultat pct |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | 14 838 000 $ | 2321 | 6 393 $ | 4 719 980 $ | 31,8 % | 2 773 398 $ | 1 204 436 $ | 210 173 $ | 531 974 $ | 3,6 % |
| 2025 | 17 463 307 $ | 2789 | 6 261 $ | 4 869 074 $ | 27,9 % | 2 772 216 $ | 1 250 639 $ | 226 879 $ | 619 340 $ | 3,5 % |

## Marge brute par famille de produits

<sub>Requete `@marge_par_famille` — `SQL/2_requetes_analyse.sql`</sub>


| famille | ca 2024 | ca 2025 | marge 2024 pct | marge 2025 pct | variation points |
|---|---|---|---|---|---|
| Vêtements techniques | 3 180 309 $ | 3 720 906 $ | 35,5 % | 25,5 % | -9,9 pts |
| Randonnée | 3 058 487 $ | 3 682 173 $ | 28,9 % | 25,2 % | -3,8 pts |
| Camping | 2 637 038 $ | 2 939 071 $ | 31,0 % | 27,4 % | -3,5 pts |
| Pêche | 1 603 998 $ | 1 722 878 $ | 24,3 % | 23,0 % | -1,4 pts |
| Sports d'hiver | 2 109 417 $ | 2 734 630 $ | 30,6 % | 29,3 % | -1,3 pts |
| Accessoires | 2 248 751 $ | 2 663 649 $ | 38,0 % | 37,1 % | -0,8 pts |

## Evolution du cout d'achat par fournisseur

<sub>Requete `@cout_achat_par_fournisseur` — `SQL/2_requetes_analyse.sql`</sub>


| fournisseur | nb articles | ca 2024 | ca 2025 | cout unitaire 2024 | cout unitaire 2025 | variation cout pct | marge 2025 |
|---|---|---|---|---|---|---|---|
| PolarTech Fabrics | 8 | 411 011 $ | 519 953 $ | 132,77 $ | 151,79 $ | +14,3 % | 142 306 $ |
| Nordik Textile inc. | 48 | 4 197 577 $ | 4 653 412 $ | 190,78 $ | 218,00 $ | +14,3 % | 1 016 526 $ |
| Rivière Bleue Pêche | 6 | 285 035 $ | 352 831 $ | 113,80 $ | 126,35 $ | +11,0 % | 90 652 $ |
| Mont-Blanc Distribution | 17 | 1 337 341 $ | 1 609 255 $ | 177,30 $ | 184,75 $ | +4,2 % | 477 845 $ |
| Vertex Gear Supply | 11 | 1 108 563 $ | 1 368 521 $ | 191,95 $ | 199,88 $ | +4,1 % | 376 100 $ |
| Delta Angling Supply | 24 | 2 226 170 $ | 2 661 130 $ | 153,93 $ | 158,42 $ | +2,9 % | 840 885 $ |
| Pacific Rim Textiles | 7 | 732 924 $ | 823 447 $ | 202,79 $ | 203,38 $ | +0,3 % | 287 139 $ |
| Saguenay Metal Works | 9 | 729 370 $ | 940 461 $ | 145,22 $ | 144,45 $ | -0,5 % | 265 031 $ |

## Manque a gagner 2025 a cout d'achat 2024

<sub>Requete `@impact_chiffre_derive` — `SQL/2_requetes_analyse.sql`</sub>


| fournisseur | ca 2025 | marge reelle 2025 | marge a cout 2024 | manque a gagner |
|---|---|---|---|---|
| Nordik Textile inc. | 4 653 412 $ | 1 016 526 $ | 1 546 433 $ | 529 906 $ |
| Delta Angling Supply | 2 661 130 $ | 840 885 $ | 878 327 $ | 37 442 $ |
| Mont-Blanc Distribution | 1 609 255 $ | 477 845 $ | 501 115 $ | 23 270 $ |
| Alpin Équipement ltée | 1 718 264 $ | 592 455 $ | 615 616 $ | 23 161 $ |
| Vertex Gear Supply | 1 368 521 $ | 376 100 $ | 396 512 $ | 20 412 $ |

## Concentration du chiffre d'affaires (top 10 clients)

<sub>Requete `@concentration_clients` — `SQL/2_requetes_analyse.sql`</sub>


| rang | nom | segment | ca | part pct | part cumulee pct |
|---|---|---|---|---|---|
| 1 | Nature Gaspésie | A | 1 256 572 $ | 3,9 % | 3,9 % |
| 2 | Coopérative Cantons | A | 1 185 443 $ | 3,7 % | 7,6 % |
| 3 | Le Refuge inc. | A | 1 088 942 $ | 3,4 % | 10,9 % |
| 4 | Aventure Vaudreuil ltée | A | 1 063 059 $ | 3,3 % | 14,2 % |
| 5 | Le Refuge Cantons | A | 1 053 414 $ | 3,3 % | 17,5 % |
| 6 | Randonneurs Appalaches | A | 1 026 955 $ | 3,2 % | 20,7 % |
| 7 | Expédition Abitibi | A | 999 119 $ | 3,1 % | 23,8 % |
| 8 | Expédition Appalaches | A | 963 249 $ | 3,0 % | 26,7 % |
| 9 | Coopérative du Nord | A | 890 495 $ | 2,8 % | 29,5 % |
| 10 | Randonneurs et Fils | A | 863 738 $ | 2,7 % | 32,2 % |

## Rotation des stocks par entrepot

<sub>Requete `@rotation_stock` — `SQL/2_requetes_analyse.sql`</sub>


| entrepot | annee | cout marchandises vendues | stock moyen | rotation | jours de stock |
|---|---|---|---|---|---|
| Saguenay | 2024 | 2 061 837 $ | 764 008 $ | 2,70 | 135 j |
| Québec | 2024 | 4 170 074 $ | 1 015 529 $ | 4,11 | 89 j |
| Montréal | 2024 | 3 886 108 $ | 616 242 $ | 6,31 | 58 j |
| Saguenay | 2025 | 2 243 896 $ | 815 449 $ | 2,75 | 133 j |
| Québec | 2025 | 5 337 967 $ | 1 080 080 $ | 4,94 | 74 j |
| Montréal | 2025 | 5 012 370 $ | 657 744 $ | 7,62 | 48 j |

## Delai moyen d'encaissement et encours client

<sub>Requete `@delai_paiement` — `SQL/2_requetes_analyse.sql`</sub>


| annee | lignes facturees | dso moyen jours | lignes non reglees | encours non regle |
|---|---|---|---|---|
| 2024 | 7193 | 40,4 j | 249 | 486 592 $ |
| 2025 | 8490 | 50,3 j | 1330 | 2 886 672 $ |

## Performance des canaux marketing

<sub>Requete `@performance_marketing` — `SQL/2_requetes_analyse.sql`</sub>


| canal | depense totale | prospects | nouveaux clients | cout par prospect | cout par client |
|---|---|---|---|---|---|
| Courriel | 26 934 $ | 1537 | 133 | 18 $ | 203 $ |
| Publicité numérique | 142 545 $ | 3120 | 152 | 46 $ | 938 $ |
| Commandite locale | 42 946 $ | 230 | 9 | 187 $ | 4 772 $ |
| Catalogue imprimé | 47 006 $ | 262 | 7 | 179 $ | 6 715 $ |
| Salons professionnels | 177 621 $ | 366 | 18 | 485 $ | 9 868 $ |

## Masse salariale rapportee au chiffre d'affaires

<sub>Requete `@masse_salariale` — `SQL/2_requetes_analyse.sql`</sub>


| annee | ca | masse salariale | effectif paye | masse sur ca pct | ca par employe |
|---|---|---|---|---|---|
| 2024 | 14 838 000 $ | 2 773 398 $ | 44 | 18,7 % | 337 227 $ |
| 2025 | 17 463 307 $ | 2 772 216 $ | 44 | 15,9 % | 396 893 $ |

## Taux de roulement par departement

<sub>Requete `@roulement_personnel` — `SQL/2_requetes_analyse.sql`</sub>


| departement | effectif total | departs | taux roulement pct |
|---|---|---|---|
| Marketing | 4 | 1 | 25,0 % |
| Entrepôt | 20 | 4 | 20,0 % |
| Administration | 8 | 1 | 12,5 % |
| Ventes | 10 | 0 | 0,0 % |
| Direction | 2 | 0 | 0,0 % |
| Approvisionnement | 3 | 0 | 0,0 % |

## Ponctualite de livraison des fournisseurs

<sub>Requete `@ponctualite_fournisseurs` — `SQL/2_requetes_analyse.sql`</sub>


| fournisseur | pays | receptions | en retard | taux retard pct | retard moyen jours |
|---|---|---|---|---|---|
| PolarTech Fabrics | Canada | 145 | 45 | 31,0 % | 8 j |
| Vertex Gear Supply | États-Unis | 137 | 40 | 29,2 % | 7,8 j |
| Nordik Textile inc. | Canada | 140 | 35 | 25,0 % | 10,9 j |
| Pacific Rim Textiles | Vietnam | 132 | 33 | 25,0 % | 8,7 j |
| Chemin Faisant inc. | Canada | 147 | 34 | 23,1 % | 10,8 j |
| Kestrel Import Group | Chine | 154 | 34 | 22,1 % | 7,6 j |
| Tundra Winter Goods | Canada | 134 | 29 | 21,6 % | 3,4 j |
| Rivière Bleue Pêche | Canada | 148 | 31 | 20,9 % | 7,3 j |

## Saisonnalite mensuelle du chiffre d'affaires

<sub>Requete `@saisonnalite` — `SQL/2_requetes_analyse.sql`</sub>


| mois | nom mois | ca 2024 | ca 2025 |
|---|---|---|---|
| 1 | janvier | 529 349 $ | 777 943 $ |
| 2 | février | 751 758 $ | 850 657 $ |
| 3 | mars | 1 236 507 $ | 1 163 810 $ |
| 4 | avril | 1 123 221 $ | 1 594 080 $ |
| 5 | mai | 1 606 633 $ | 1 515 111 $ |
| 6 | juin | 1 120 539 $ | 1 511 218 $ |
| 7 | juillet | 978 437 $ | 1 084 188 $ |
| 8 | août | 1 641 381 $ | 1 708 081 $ |
| 9 | septembre | 1 909 337 $ | 2 299 273 $ |
| 10 | octobre | 1 950 025 $ | 2 154 647 $ |
| 11 | novembre | 1 223 144 $ | 1 686 016 $ |
| 12 | décembre | 767 668 $ | 1 118 282 $ |

## Journal de nettoyage par nature de defaut

<sub>Requete `@qualite_donnees` — `SQL/2_requetes_analyse.sql`</sub>


| motif | lignes rejetees | valeurs traitees | total |
|---|---|---|---|
| variante_ecriture | 0 | 552 | 552 |
| casse_ou_espaces | 0 | 370 | 370 |
| doublon_exact | 277 | 0 | 277 |
| valeur_manquante | 0 | 162 | 162 |
| article_inconnu | 135 | 0 | 135 |
| date_illisible | 92 | 0 | 92 |
| quantite_invalide | 76 | 0 | 76 |
| quantite_negative | 0 | 38 | 38 |
| nombre_en_texte | 0 | 31 | 31 |
| prix_invalide | 31 | 0 | 31 |
| prix_aberrant | 26 | 0 | 26 |
| doublon_metier | 0 | 14 | 14 |
| courriel_invalide | 0 | 9 | 9 |
| cout_standard_absent | 0 | 5 | 5 |
| ligne_technique | 5 | 0 | 5 |
