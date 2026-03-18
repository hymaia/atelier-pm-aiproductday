# pm-discovery — Discovery & recherche utilisateur

## RÈGLE ABSOLUE — Anti-hallucination
Ne jamais répondre à une question sur des données sans avoir exécuté le script correspondant.
Si le script retourne "AUCUNE DONNÉE", répondre exactement cela à l'utilisateur sans inventer.
Toujours indiquer quelle source a été consultée.

## Skills disponibles

### fetch-interviews
Utiliser quand l'utilisateur demande :
- Les verbatims ou retours d'un utilisateur, client ou persona
- Les interviews sur un thème précis (performance, mobile, onboarding...)
- Les interviews d'une période donnée

### fetch-opportunities
Utiliser quand l'utilisateur demande :
- Les opportunités produit identifiées
- Les pain points récurrents
- Ce qu'il faut retenir de la recherche utilisateur
- Une synthèse des insights

## Architecture
```
pm-discovery/
├── CLAUDE.md
├── requirements.txt
├── data/
│   └── interviews/        ← transcriptions .md par persona/client + date
├── utils/
│   └── interview_loader.py
└── .claude/skills/
    ├── fetch-interviews/
    │   ├── SKILL.md
    │   └── fetch_interviews.py
    └── fetch-opportunities/
        ├── SKILL.md
        └── fetch_opportunities.py
```
