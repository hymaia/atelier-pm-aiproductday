# pm-data-analyze — Analyse de données

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Analyse de métriques produit (activation, rétention, conversion)
- Résumé de dashboards et KPIs
- Détection d'anomalies et tendances
- Comparaisons entre périodes

## Structure prévue
```
pm-data-analyze/
  data/
    metrics/                  # exports CSV de métriques
    dashboards/               # snapshots de dashboards
  utils/                      # loaders partagés entre skills
  .claude/skills/
    analyze-metrics/
      SKILL.md                # user-invocable: false
      fetch_metrics.py        # glob data/, retourne texte brut
    summarize-kpis/
      SKILL.md                # user-invocable: false
      fetch_kpis.py           # glob data/, retourne texte brut
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur des données ou métriques, répondre :
"Le module pm-data-analyze est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
