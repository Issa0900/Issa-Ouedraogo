---
layout: project
title: Intégration IA au flux de travail
---

# 🤖 Intégration IA au flux de travail

![IA appliquée](https://img.shields.io/badge/IA_appliquée-Claude_Code-0B6B45?style=flat)
![Statut](https://img.shields.io/badge/Statut-Pratique_continue-informational)

Diriger l'IA générative pour produire du code et des analyses fiables est une compétence à part entière : spécifier ce qui doit être construit, repérer ce qui ne va pas dans un résultat généré, et savoir quand une réponse rapide cache un problème de fond. C'est cette compétence que ce projet documente.

## 🎯 Ce que ça demande concrètement

Utiliser l'IA en production ne dispense pas de comprendre ce qu'elle produit, au contraire, ça exige de le comprendre assez bien pour la corriger. Trois réflexes reviennent dans chaque exemple ci-dessous :

- **Spécifier précisément** : un résultat correct commence par un problème correctement posé, pas par un prompt vague.
- **Vérifier plutôt que supposer** : chaque résultat généré est testé, relu, confronté aux données réelles avant d'être considéré fini.
- **Reconnaître ce qui cloche** : la valeur ajoutée est de repérer la race condition, le seuil mal choisi ou le calcul faux qu'une lecture rapide laisserait passer.

## 📌 Preuves à l'appui

### Copilote PME : décisions d'ingénierie

Sur le MVP full-stack de [Copilote PME](https://github.com/Issa0900/copilote-pme), j'ai dirigé la construction de l'authentification, du pipeline d'ingestion et du moteur de détection d'anomalies avec Claude Code comme exécutant ; les décisions d'architecture et les corrections restent les miennes :

- [Détection d'anomalies par médiane/MAD plutôt qu'un seuil fixe](https://github.com/Issa0900/copilote-pme/commit/cafc645) : un seuil fixe génère trop de faux positifs sur des données réelles de PME, ce choix de méthode vient de l'analyse du comportement des données, pas d'une suggestion par défaut.
- [Identification et correction d'une race condition](https://github.com/Issa0900/copilote-pme/commit/2aa9345) sur des requêtes concurrentes : un bug qui n'apparaît qu'avec plusieurs utilisateurs simultanés, repéré en anticipant ce cas plutôt qu'en testant seulement le chemin nominal.
- [Authentification JWT et isolation multi-tenant](https://github.com/Issa0900/copilote-pme/commit/6fe0bab) : spécification des règles d'accès entre entreprises avant l'implémentation.
- [Ingestion OCR pour les PDF scannés](https://github.com/Issa0900/copilote-pme/commit/a901733), pour couvrir un format de document réel qu'une PME utilise encore couramment.

### Analyses statistiques : la vérification comme discipline

Sur [Analyse statistique et tests d'hypothèses](../analyse-statistique-inferentielle/), l'assistance a porté sur l'écriture des scripts ; la méthode (tests d'hypothèses, corrélation, intervalles de confiance) et sa validation sont de moi. Exigence posée dès le départ : recalculer les 36 contrôles croisés indépendamment du classeur d'origine, résultat, zéro écart. C'est ce niveau de vérification qui distingue un résultat utilisable d'un résultat qui a l'air correct.

### Ce portfolio

La structure du site (page d'accueil, gabarit de projet, système de design partagé) a été construite avec Claude Code sur la base de choix de contenu et de priorisation que j'ai fixés : quels projets mettre en avant, quel message porter en premier, quelle hiérarchie d'information. [Refonte du design](https://github.com/Issa0900/Issa-Ouedraogo/commit/e635e02), [repositionnement du contenu](https://github.com/Issa0900/Issa-Ouedraogo/commit/77b6060).

## 💡 Pourquoi ça compte pour une PME

Une PME qui a besoin d'un outil d'analyse n'a généralement ni le budget ni le temps pour une équipe de développement complète. Savoir diriger l'IA pour produire un livrable fiable, pas seulement un livrable rapide, réduit ce délai sans sacrifier la rigueur : c'est exactement le type d'écart qui sépare un prototype qu'on jette d'un outil qu'on garde.
