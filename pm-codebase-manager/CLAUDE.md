# pm-codebase-manager — Exploration et compréhension du code

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Lire et expliquer du code source en langage accessible pour un PM
- Répondre à des questions sur le fonctionnement technique d'une feature
- Résumer ce que les devs ont livré (PRs, commits, changelogs)
- Identifier les impacts produit d'un changement technique

## Structure prévue
```
pm-codebase-manager/
  data/
    source/                   # fichiers de code à expliquer (.py, .ts, .js...)
    releases/                 # changelogs, release notes (.md, .txt)
    pull_requests/            # exports de PRs (GitHub, GitLab)
  utils/                      # loaders partagés entre skills
  .claude/skills/
    explain-code/
      SKILL.md                # user-invocable: false
      fetch_code.py           # glob data/, retourne le code brut
    summarize-releases/
      SKILL.md                # user-invocable: false
      fetch_releases.py       # glob data/, retourne texte brut
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur du code, une release ou un changement technique,
répondre : "Le module pm-codebase-manager est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
