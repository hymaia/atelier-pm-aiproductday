# pm-dev-bridge — Compréhension du travail dev & prototypage

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Lire et résumer ce que les devs ont livré (PRs, commits, changelogs, release notes)
- Traduire le travail technique en langage produit (pour des stakeholders non-techniques)
- Prototyper de nouvelles fonctionnalités : rédiger des specs, user stories, critères d'acceptance
- Détecter les écarts entre ce qui était prévu (tickets) et ce qui a été livré

## Structure prévue
```
pm-dev-bridge/
  skills/
    summarize_releases.py     # résumé des livraisons récentes
    generate_spec.py          # génération de spec à partir d'une idée
  data/
    releases/                 # changelogs, release notes (.md, .txt)
    pull_requests/            # exports de PRs (GitHub, GitLab)
    specs/                    # specs et user stories générées
  index.json
  indexer.py
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur ce que les devs ont livré, sur une release,
ou veut prototyper une fonctionnalité, répondre :
"Le module pm-dev-bridge est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
