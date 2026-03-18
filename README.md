# PM AI Assistant — Workspace

Assistant IA pour Product Managers, construit sur Claude Code.
Ce workspace regroupe plusieurs modules spécialisés, chacun couvrant un domaine du quotidien d'un PM.

## Modules

| Module | Statut | Description |
|---|---|---|
| `pm-meeting-assistant/` | ✅ Disponible | Briefing du matin, préparation de réunions |
| `pm-inbox/` | ✅ Disponible | Triage des emails et messages Slack, brouillons de réponse |
| `pm-tickets-analyze/` | 🚧 En construction | Analyse de tickets Jira/Linear, backlogs |
| `pm-discovery/` | 🚧 En construction | Synthèse interviews, insights utilisateurs |
| `pm-data-analyze/` | 🚧 En construction | Métriques, KPIs, dashboards |
| `pm-dev-bridge/` | 🚧 En construction | Releases, PRs, specs, user stories |

## Utilisation

Ouvrir le dossier racine dans Claude Code et poser une question naturellement.
Claude identifie automatiquement le bon module et le bon skill à utiliser.

```
"C'est quoi mon agenda du 17 mars ?"
"Est-ce que j'ai des mails urgents ?"
"Prépare-moi la réunion avec Carrefour."
```

## Architecture

Chaque module suit la même structure :

```
pm-xxx/
├── CLAUDE.md              ← instructions et routing
├── requirements.txt       ← dépendances Python du module
├── data/                  ← données mockées
├── utils/                 ← loaders partagés entre les scripts
└── .claude/skills/        ← skills Claude Code
    └── nom-du-skill/
        ├── SKILL.md       ← instructions pour Claude
        └── fetch_xxx.py   ← script de récupération des données
```

## Contexte PM

Le profil du PM (rôle, style, clients, priorités) est dans `context/pm_profile.md`.
Il est utilisé par les skills qui génèrent du contenu personnalisé (ex: brouillons de réponse).
