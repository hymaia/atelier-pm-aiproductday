# pm-tickets-analyze — Analyse de tickets

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Analyse de tickets Jira / Linear / GitHub Issues
- Détection de tendances dans le backlog
- Résumé des tickets bloquants ou en retard
- Priorisation assistée

## Structure prévue
```
pm-tickets-analyze/
  skills/
    analyze_backlog.py      # tendances et état du backlog
    summarize_sprint.py     # résumé de sprint
  data/
    tickets/                # exports CSV/JSON de tickets
  index.json                # index des fichiers
  indexer.py                # indexeur local
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur des tickets, répondre :
"Le module pm-tickets-analyze est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
