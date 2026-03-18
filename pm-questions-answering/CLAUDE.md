# pm-questions-answering — Q&A sur la documentation

🚧 **Module en construction** — Aucun skill disponible pour l'instant.

## Périmètre prévu
- Réponses aux questions sur les PRDs et specs produit
- Recherche dans la documentation interne
- Résumé de documents longs
- Vérification de cohérence entre specs

## Structure prévue
```
pm-questions-answering/
  data/
    specs/                    # PRDs, specs (.md, .pdf, .docx)
    wikis/                    # exports Notion/Confluence
  utils/                      # loaders partagés entre skills
  .claude/skills/
    answer-question/
      SKILL.md                # user-invocable: false
      fetch_docs.py           # glob data/, retourne texte brut
```

## Instructions pour Claude Code
Si l'utilisateur pose une question sur de la documentation produit, répondre :
"Le module pm-questions-answering est en construction. Aucun skill n'est disponible pour l'instant."
Ne pas inventer de réponse à partir d'autres sources.
