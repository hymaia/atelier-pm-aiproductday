---
slide: 02
title: Le projet Product Day
subtitle: Un OS IA modulaire pour PM
---

## Story Map

| Module | Statut | Context (données) | Tools (code) | Skills (commandes) |
|--------|--------|-------------------|--------------|---------------------|
| **meeting-assistant** | ✅ | Calendrier CSV · Transcripts TXT · Notes MD · Résumés CSV | indexer.py · 4 loaders | `/morning-briefing` · `/prepare-meeting` |
| **tickets-analyze** | 🚧 | Tickets Jira/Linear CSV | indexer.py · JSON/CSV loader | `/analyze-backlog` · `/summarize-sprint` |
| **discovery** | 🚧 | Interviews TXT/MD · Insights | indexer.py · TXT/MD loader | `/synthesize-interviews` · `/extract-insights` |
| **questions-answering** | 🚧 | Specs PDF · PRDs MD · Wikis | indexer.py · PDF/DOCX loader | `/answer-question` · `/search-docs` |
| **data-analyze** | 🚧 | Métriques CSV · Dashboards | indexer.py · CSV loader | `/analyze-metrics` · `/summarize-kpis` |
| **dev-bridge** | 🚧 | PRs · Changelogs MD · Releases | indexer.py · MD/JSON loader | `/summarize-releases` · `/generate-spec` |

## Légende
- **Context** : les données que vous apportez (vos fichiers)
- **Tools** : le code qui indexe et lit vos données
- **Skills** : les commandes que vous tapez dans Claude Code
