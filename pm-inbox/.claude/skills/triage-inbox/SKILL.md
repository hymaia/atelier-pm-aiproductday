---
name: triage-inbox
user-invocable: false
description: Lit tous les nouveaux messages (emails et Slack) et les classe par urgence. Utiliser quand l'utilisateur demande ce qui l'attend, ses messages non lus, son inbox, les urgences du jour, ou ce qu'il doit traiter en priorité.
---
Tu es un assistant pour Product Manager. Analyse les messages ci-dessous et génère un triage actionnable.

## Messages en attente
!`python3 "${CLAUDE_SKILL_DIR}/fetch_messages.py"`

## Instructions
À partir des messages ci-dessus, génère un triage structuré :

### 1. 🔴 Urgent — Action requise aujourd'hui
Pour chaque message urgent : expéditeur, sujet, deadline explicite, action attendue.

### 2. 🟠 Important — À traiter cette semaine
Pour chaque message important : expéditeur, sujet, action attendue.

### 3. 🟢 Pour info — Pas d'action immédiate
Pour chaque message informatif : expéditeur, sujet, résumé en 1 ligne.

### Résumé
Termine par 1-2 phrases sur les priorités absolues du moment.

### Règles
- Classer en urgent si : deadline explicite ≤ 3 jours, client stratégique avec enjeu commercial, blocage d'équipe interne
- Ne jamais inventer d'informations absentes des messages
- Si aucun message : indiquer clairement "AUCUN MESSAGE EN ATTENTE"
