---
slide: 03
title: Démo live
subtitle: Un PM et son OS IA
---

## Ce qu'on va faire ensemble

On bascule sur Claude Code pour montrer un PM qui interagit avec son assistant.

### Étape 1 — Indexer les données
```bash
cd pm-meeting-assistant
python3 indexer.py
```

### Étape 2 — Lancer Claude Code
```bash
claude
```

### Étape 3 — Briefing du matin
```
/morning-briefing
```
→ Claude lit l'agenda, croise avec l'historique client, génère le briefing.

### Étape 4 — Préparer une réunion
```
/prepare-meeting acme
```
→ Claude récupère les notes, transcripts et actions ouvertes pour Acme.

## Ce que ça montre
- Claude lit VOS données locales (pas internet)
- Il suit des instructions précises (CLAUDE.md)
- Il exécute du code Python pour récupérer le contexte
- Zéro hallucination : si pas de données, il le dit
