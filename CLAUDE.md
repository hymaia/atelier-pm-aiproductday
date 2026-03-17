# PM Meeting Assistant — Instructions pour Claude Code

Ce projet est un assistant pour Product Managers. Quand l'utilisateur pose une question,
exécute automatiquement le bon skill Python sans lui demander de taper une commande slash.

## Répertoire de travail
Toujours exécuter les commandes depuis :
`/Users/vincentgadanho/Documents/Software/Ai Product Day Claude Code Workshop/pm-meeting-assistant`

## Règles de routage automatique

### Briefing / agenda / réunions du jour
Si l'utilisateur demande son agenda, son briefing, ses réunions, ce qu'il a aujourd'hui
ou pour une date précise → exécuter :
```
python3 skills/morning_briefing.py [YYYY-MM-DD]
```
Si aucune date n'est mentionnée, utiliser la date du jour.

### Préparer une réunion / fiche client
Si l'utilisateur mentionne un client (Acme, Carrefour, NovaTech), un participant,
ou demande de se préparer pour un call → exécuter :
```
python3 skills/prepare_meeting.py "nom du client ou participant"
```

## Comportement attendu
- Ne pas demander confirmation avant d'exécuter
- Afficher directement le résultat du script
- Si la question est ambiguë, choisir le skill le plus probable et l'exécuter
