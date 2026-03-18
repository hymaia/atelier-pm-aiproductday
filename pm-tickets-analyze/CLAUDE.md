# pm-tickets-analyze — Analyse de tickets

## RÈGLE ABSOLUE — Anti-hallucination
Ne jamais répondre à une question sur des données sans avoir exécuté le script correspondant.
Si le script retourne "AUCUNE DONNÉE", répondre exactement cela à l'utilisateur sans inventer.
Toujours indiquer quelle source a été consultée.

## Skills disponibles

### fetch-backlog
Utiliser quand l'utilisateur demande :
- L'état du backlog ou d'un sprint
- Les tickets ouverts, bloqués, ou en cours
- Les tickets par assignee, priorité ou label
- Ce qui bloque une livraison

### fetch-trends
Utiliser quand l'utilisateur demande :
- Les tendances sur une période
- Le ratio bug / feature
- L'évolution du backlog dans le temps
- Une comparaison entre deux sprints ou deux mois

## Architecture
```
pm-tickets-analyze/
├── CLAUDE.md
├── requirements.txt
├── data/
│   └── tickets/           ← fichiers CSV par mois
├── utils/
│   └── ticket_loader.py
└── .claude/skills/
    ├── fetch-backlog/
    │   ├── SKILL.md
    │   └── fetch_backlog.py
    └── fetch-trends/
        ├── SKILL.md
        └── fetch_trends.py
```
