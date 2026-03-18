# pm-codebase-manager — Compréhension du code & releases

## RÈGLE ABSOLUE — Anti-hallucination
Ne jamais répondre à une question sur du code ou une release sans avoir exécuté le script correspondant.
Si le script retourne "AUCUNE DONNÉE", répondre exactement cela à l'utilisateur sans inventer.
Toujours indiquer quel fichier a été consulté.

## Skills disponibles

### explain-code
Utiliser quand l'utilisateur demande :
- Comment fonctionne une feature ou un endpoint technique
- Ce que fait un fichier de code spécifique
- Les limites ou règles d'une API (rate limits, taille de batch...)
- L'impact produit d'un choix technique

### summarize-releases
Utiliser quand l'utilisateur demande :
- Ce qui a été livré dans une version ou un sprint
- Les nouveautés récentes de la plateforme
- L'impact d'une release sur un client spécifique
- Un résumé des changelogs pour une présentation

## Architecture
```
pm-codebase-manager/
├── CLAUDE.md
├── requirements.txt
├── data/
│   ├── source/                    ← fichiers de code source (.py, .ts, .js...)
│   │   ├── products_api.py        — API batch Acme Corp
│   │   ├── webhook_handler.ts     — Webhooks NovaTech
│   │   └── dashboard_cache.py     — Cache Redis Carrefour Digital
│   └── releases/                  ← changelogs et release notes (.md)
│       ├── changelog_v2.3.md      — Webhooks + API batch (mars 2026)
│       └── changelog_v2.2.md      — Cache dashboards (février 2026)
├── utils/
│   ├── __init__.py
│   ├── code_loader.py             — load(filepath) → dict {filename, language, content}
│   └── release_loader.py         — load(filepath) → dict {filename, version, date, content}
└── .claude/skills/
    ├── explain-code/
    │   ├── SKILL.md               — user-invocable: false
    │   └── fetch_code.py          — glob data/source/, filtre par query, retourne code brut
    └── summarize-releases/
        ├── SKILL.md               — user-invocable: false
        └── fetch_releases.py      — glob data/releases/, filtre par query, retourne changelog brut
```
