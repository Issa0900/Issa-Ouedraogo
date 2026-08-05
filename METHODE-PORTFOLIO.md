# Méthode — Construire et publier un projet data sur mon portfolio GitHub

Ce fichier documente le mode de travail à réutiliser pour chaque nouveau projet data (dashboard Excel, analyse, rapport) ajouté au portfolio GitHub. À partager à Claude en début de conversation pour qu'il applique la même méthode sans repartir de zéro.

## Phase 1 — Construire le livrable (ex. dashboard Excel)

1. **Nettoyer les données d'abord**, documenter chaque anomalie corrigée (encodage, séparateurs décimaux incohérents `,`/`.`, lignes de bruit/totaux en fin de fichier, valeurs manquantes) avec les volumes avant/après. Ce sont des insights à part entière pour le README plus tard.
2. **Si le livrable est un classeur Excel généré par script (`openpyxl`)** :
   - Écrire les données en **bulk** (`ws.append(row)` par ligne) plutôt que cellule par cellule — bien plus rapide sur des tables de plusieurs milliers de lignes.
   - **Formules : utiliser les noms de fonctions canoniques anglais** (`SUM`, `SUMIF`, `SUMIFS`, `AVERAGE`, `VLOOKUP`, `MATCH`, `COUNTA`, `COUNTIFS`, `IFERROR`, `INDEX`) même si le classeur est en français — Excel les traduit automatiquement à l'affichage selon la locale. Écrire `SOMME.SI.ENS(...)` littéralement produit un `#NAME?`.
   - **Éviter `SUMPRODUCT` avec des `IF(...)` imbriqués sur de grandes plages** (filtre dynamique "Tous" vs valeur précise) — très lent à recalculer. Préférer `SUMIFS` avec critère `"<>"` (non-vide) quand le filtre = "Tous" : `=SUMIFS(plage_somme, plage_critere, IF(cellule_filtre="Tous","<>",cellule_filtre))`.
   - **Segments/slicers interactifs sans TCD natif** : `openpyxl` ne peut pas créer de vrais Slicers Excel liés à un TCD natif. Utiliser des listes déroulantes (`DataValidation`) pilotant des formules SUMIFS — même expérience utilisateur, 100% scriptable. Documenter ce choix dans le classeur et le README.
   - **Graphiques** : un `PieChart` avec `dataLabels` par défaut affiche nom + valeur brute (illisible) sauf si on force `showCatName=False`, `showSerName=False`, `showVal=False`, `showLegendKey=False`, `showPercent=True`. Pour un bar chart horizontal "Top N", penser à `y_axis.scaling.orientation = "maxMin"` sinon la plus grande valeur s'affiche en bas.
   - **Recalcul (LibreOffice headless)** : ajouter les graphiques APRÈS avoir recalculé et vérifié `total_errors: 0` sur les formules — les ajouter avant ralentit fortement le recalcul et cause des timeouts. Mettre `wb.calculation.fullCalcOnLoad = True` pour qu'Excel recalcule tout automatiquement à l'ouverture, même si le cache de certaines cellules a été perdu en cours de route.
   - Toujours vérifier avec `data_only=True` que les cellules clés renvoient la bonne valeur (pas juste l'absence d'erreur `#NAME?`) — un bug classique est une formule de marge/ratio qui référence la mauvaise cellule après une fusion (`merge_cells`).
3. **Toujours croiser les chiffres clés avec un calcul indépendant** (ex. `pandas.groupby(...).sum()`) avant de les citer dans le README.

## Phase 2 — Écrire le README portfolio

Structure qui fonctionne bien :

1. Titre + badges technos (shields.io) + statut
2. Résumé en une phrase + lien vers le livrable
3. Contexte métier (le problème business, pas juste "voici des données")
4. Objectif du projet
5. Données : source, période, volume, nettoyage effectué (avant/après)
6. Compétences techniques démontrées (liste concrète)
7. Structure du livrable (table des onglets/fichiers et leur contenu)
8. **Insights clés avec de vrais chiffres calculés** — jamais de valeurs inventées, formulés comme des observations business
9. Comment tester/utiliser le livrable soi-même
10. Choix méthodologiques notables (limitations d'outils contournées — bon point pour un entretien)
11. Contact

## Phase 3 — Publier sur GitHub et VÉRIFIER (étape critique, souvent sautée)

**GitHub ne prévisualise pas correctement les fichiers Excel complexes** (formules nombreuses, graphiques, feuilles masquées, validation de données) → erreur de chargement. Ce n'est pas un fichier corrompu, c'est une limite du viewer GitHub. Solutions à combiner dans le README :
- Un lien **"Ouvrir en ligne"** : `https://view.officeapps.live.com/op/view.aspx?src=<URL RAW encodée>` où l'URL raw est `https://raw.githubusercontent.com/<user>/<repo>/<branche>/<chemin-fichier>`.
- Des **images d'aperçu statiques** intégrées directement dans le README. Si une vraie capture n'est pas disponible (fichier verrouillé, rendu headless trop lent/instable), générer un aperçu fidèle avec `matplotlib` reproduisant la mise en page réelle avec les **vraies données calculées**.
- Pour démontrer l'interactivité (filtres/segments) : générer deux images côte à côte (état par défaut / état filtré) avec les vrais chiffres recalculés.

**Après upload par l'utilisateur, ne jamais supposer que c'est bon — toujours vérifier en direct :**
1. Aller voir l'arborescence réelle du repo (`https://github.com/<user>/<repo>`).
2. **Comparer les chemins réels avec ceux référencés dans le README.** Erreur la plus fréquente : le README référence `./assets/image.png` mais l'image a été uploadée à la racine (`image.png`) — corriger le README pour coller à la structure réelle plutôt que d'imposer une réorganisation à l'utilisateur.
3. Vérifier que la version du README en ligne est bien la dernière (l'utilisateur oublie parfois de committer après avoir collé le contenu).
4. Vérifier qu'un fichier image s'ouvre bien directement (taille non nulle, pas de page d'erreur).
5. Ne déclarer "fonctionnel" qu'après avoir vu ces vérifications passer.

## Limites d'environnement à connaître (génération de fichiers via script)

- Les commandes shell ont un timeout dur (~45s) et aucun processus en arrière-plan ne survit entre deux commandes — découper un traitement long en plusieurs scripts séquentiels avec checkpoints sur disque.
- Un fichier dans le dossier livrable peut être verrouillé en écriture s'il est ouvert dans Excel — demander de le fermer plutôt que de conclure à une erreur. Une suppression peut aussi nécessiter une permission explicite.
