---
layout: project
title: Intégration IA au flux de travail
---

# 🤖 Intégration IA au flux de travail

![IA appliquée](https://img.shields.io/badge/IA_appliquée-Claude_Code-0B6B45?style=flat)
![Statut](https://img.shields.io/badge/Statut-Pratique_continue-informational)

Intégrer l'IA générative à un flux de travail, ce n'est pas lui poser une question et copier la réponse. C'est un processus en quatre étapes, répété à chaque tâche, avec un rôle précis pour l'humain à chacune. Ce projet documente ce processus tel que je l'applique, avec des preuves tirées de mes propres projets à chaque étape.

## 🔄 Le processus en quatre étapes

### 1. Cadrage

Avant de solliciter l'IA, le problème doit être posé précisément : quel résultat, selon quels critères, avec quelles contraintes. Un prompt vague produit un résultat vague. Exemple : sur [GESCOP](../gescop/), les règles de traitement des doublons (conservés et signalés, jamais supprimés en silence) ont été décidées avant d'écrire la moindre ligne de détection.

### 2. Génération assistée

L'IA écrit le code, le script ou le texte à partir du cadrage. C'est l'étape la plus rapide du processus, et la moins déterminante pour la qualité du résultat final : la génération vaut ce que valent le cadrage et la vérification qui l'entourent.

### 3. Vérification

Chaque résultat généré est testé, relu et confronté aux données réelles avant d'être considéré fini. C'est l'étape où se joue la fiabilité du livrable. Deux exemples concrets :

- Sur [Analyse statistique et tests d'hypothèses](../analyse-statistique-inferentielle/), l'exigence posée dès le départ était de recalculer les 36 contrôles croisés indépendamment du classeur d'origine, résultat, zéro écart.
- Sur [GESCOP](../gescop/), des erreurs apparaissaient sur de vrais fichiers alors que tout semblait correct. La vérification a montré qu'elles venaient du moment où l'IA intervient. Résultat : l'application reste juste même quand l'IA se trompe ou ne répond pas, et chaque correction est vérifiée sur l'ensemble des fichiers de référence.

### 4. Intégration et livraison

Le résultat vérifié est intégré au produit ou au livrable final, documenté pour qu'il reste compréhensible plus tard. La structure de ce portfolio (page d'accueil, gabarit de projet, système de design partagé) a été construite ainsi, à partir de choix de contenu et de priorisation fixés en amont : [refonte du design](https://github.com/Issa0900/Issa-Ouedraogo/commit/e635e02), [repositionnement du contenu](https://github.com/Issa0900/Issa-Ouedraogo/commit/77b6060).

## 📌 Autres exemples appliqués

- [GESCOP](../gescop/) : reconnaissance automatique des colonnes de fichiers hétérogènes, fiable même quand les colonnes sont renommées, déplacées ou mal formatées.
- Scripts d'extraction et de visualisation pour [Geomarketing Québec](../geomarketing-quebec/), à partir d'un cadrage sur les indicateurs à produire (score d'opportunité par région).

## 💡 Pourquoi ce processus compte pour une PME

Une PME qui a besoin d'un outil d'analyse n'a généralement ni le budget ni le temps pour une équipe de développement complète. Un flux de travail qui intègre l'IA à chaque étape, cadrage, génération, vérification, livraison, réduit le délai de production sans sacrifier la rigueur. C'est cet écart, entre un prototype rapide et un outil fiable, que ce processus est conçu pour combler.
