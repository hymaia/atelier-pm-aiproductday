# pm-discovery — Discovery & recherche utilisateur

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Synthèse d'interviews utilisateurs
- Extraction d'insights et d'opportunités produit
- Regroupement de verbatims par thème
- Suivi des hypothèses de discovery

## Structure prévue
```
pm-discovery/
  data/
    interviews/               # transcriptions d'interviews (.txt, .md)
    insights/                 # notes de discovery
  utils/                      # loaders partagés entre skills
  .claude/skills/
    synthesize-interviews/
      SKILL.md                # user-invocable: false
      fetch_interviews.py     # glob data/, retourne texte brut
    extract-insights/
      SKILL.md                # user-invocable: false
      fetch_insights.py       # glob data/, retourne texte brut
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur des interviews ou la discovery, répondre :
"Le module pm-discovery est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
