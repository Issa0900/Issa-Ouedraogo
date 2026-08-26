---
layout: project
title: Intégration IA au flux de travail
---

# 🤖 Intégration IA au flux de travail

![IA appliquée](https://img.shields.io/badge/IA_appliquée-Claude_Code-0B6B45?style=flat)
![Statut](https://img.shields.io/badge/Statut-Pratique_continue-informational)

Je travaille avec l'IA générative (Claude Code) comme un collaborateur de production, pas comme un générateur de contenu final : elle accélère l'écriture de code et de rapports, je reste responsable de chaque décision et de chaque résultat publié.

## 🧩 Pourquoi

Le nettoyage de données, l'écriture de scripts répétitifs et la mise en forme de rapports prennent du temps qui devrait aller à l'interprétation et à la recommandation — la partie du travail qui crée réellement de la valeur pour une entreprise. L'IA déplace ce temps de la production vers l'analyse.

## 🎯 Où c'est utilisé concrètement

Trois usages, avec preuve à l'appui plutôt qu'une affirmation générale.

### 1. Développement logiciel — Copilote PME

Le MVP full-stack de [Copilote PME](https://github.com/Issa0900/copilote-pme) a été construit en binôme avec Claude Code : 14 des 17 commits du dépôt portent une co-attribution explicite. Quelques exemples de ce qui a été livré ainsi — pas juste du code généré, de vraies corrections avec une cause identifiée :

- [Authentification JWT et isolation multi-tenant](https://github.com/Issa0900/copilote-pme/commit/6fe0bab)
- [Correction d'une race condition sur des requêtes concurrentes](https://github.com/Issa0900/copilote-pme/commit/2aa9345) — deux onglets ouverts en même temps pouvaient déclencher une erreur d'intégrité en base
- [Ingestion OCR pour les PDF scannés sans couche de texte](https://github.com/Issa0900/copilote-pme/commit/a901733)
- [Détection d'anomalies par médiane/MAD plutôt qu'un seuil fixe](https://github.com/Issa0900/copilote-pme/commit/cafc645)

### 2. Analyses statistiques et géomarketing

Les projets [Analyse statistique et tests d'hypothèses](../analyse-statistique-inferentielle/) et [Geomarketing Québec](../geomarketing-quebec/) ont été construits avec l'assistance de Claude pour l'écriture des scripts d'extraction et de visualisation — la méthode statistique (tests d'hypothèses, corrélation, modélisation de score) et la validation des résultats restent de moi : le projet statistique recalcule ses 36 contrôles croisés indépendamment du classeur d'origine, à zéro d'écart, précisément pour vérifier que l'assistance n'a rien laissé passer.

### 3. Ce portfolio lui-même

La structure du site (page d'accueil, gabarit de projet, système de design partagé) a été développée avec Claude Code plutôt qu'à la main — [refonte du design](https://github.com/Issa0900/Issa-Ouedraogo/commit/e635e02), [repositionnement du contenu](https://github.com/Issa0900/Issa-Ouedraogo/commit/77b6060).

## ⚖️ Ce que ça ne veut pas dire

Ce n'est pas une revendication de compétence en développement logiciel au même titre qu'un développeur formé — c'est une pratique de production assistée, avec relecture et validation humaines à chaque étape. La distinction compte : je ne présente jamais une sortie d'IA comme un résultat sans l'avoir vérifiée moi-même.
