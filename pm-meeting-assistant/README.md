# PM Meeting Assistant

Outil de démonstration pour Product Managers. Déposez vos fichiers de données de réunions et discutez naturellement avec Claude pour obtenir :

1. **Briefing du matin** — Agenda du jour avec contexte de chaque réunion
2. **Préparation de réunion** — Historique, participants, last touchpoint, actions ouvertes

Propulsé par **Claude Code** (Anthropic) — aucune clé API requise, aucune commande à lancer.

---

## Utilisation

1. Ouvrir **Claude Code** à la racine du workspace (`Ai Product Day Claude Code Workshop/`)
2. Poser vos questions en langage naturel :

```
"Donne-moi mon briefing du 17 mars"
"Prépare-moi la réunion avec Carrefour"
"Qu'est-ce que j'ai aujourd'hui ?"
"Quel est l'historique avec NovaTech ?"
```

Claude détecte automatiquement le bon skill et charge les données correspondantes.

---

## Structure du projet

```
pm-meeting-assistant/
├── data/
│   ├── calendar/          # CSV agenda (une ligne par réunion)
│   ├── transcripts/       # Transcriptions .txt
│   ├── notes/             # Notes .md
│   └── summaries/         # Comptes-rendus CSV (décisions + actions)
├── utils/
│   ├── calendar_loader.py
│   ├── transcript_loader.py
│   ├── notes_loader.py
│   └── summary_loader.py
└── .claude/skills/
    ├── morning-briefing/
    │   ├── SKILL.md               # Instructions pour Claude
    │   └── fetch_agenda.py        # Charge les données du jour
    └── prepare-meeting/
        ├── SKILL.md               # Instructions pour Claude
        └── fetch_client_history.py # Charge l'historique client
```

---

## Format des fichiers de données

### Calendrier CSV (`data/calendar/`)

```csv
date,start_time,end_time,title,participants,location,description
2026-03-17,09:00,09:45,Sync produit Acme,Alice;Bob;Sarah (Acme),Zoom,Point hebdomadaire
```

> Les participants externes doivent inclure leur société entre parenthèses : `Sarah Kim (Acme)`

### Transcription TXT (`data/transcripts/`)

```
Date: 2026-03-10
Titre: Sync produit Acme Corp
Participants: Alice Martin, Bob Leroy, Sarah Kim (Acme)

[Contenu de la transcription...]
```

### Compte-rendu CSV (`data/summaries/`)

```csv
date,participants,title,decisions,actions,status
2026-03-10,"Alice, Bob, Sarah",Sync Acme,"Décision 1; Décision 2","Alice : préparer doc [OPEN]; Bob : envoyer email [DONE]",done
```

> Les actions non résolues doivent contenir `[OPEN]` pour être détectées.

### Notes Markdown (`data/notes/`)

```markdown
# Titre de la réunion
**Date :** 1er mars 2026
**Participants :** Alice Martin, Marc Dupont

## Actions
- [ ] Alice : préparer le deck
- [x] Marc : envoyer les métriques
```

---

## Convention de nommage des fichiers

```
{client}_{YYYY-MM-DD}.{ext}

Exemples :
  acme_2026-03-10.txt
  carrefour_2026-02-25.csv
  novatech_2026-03-05.txt
  calendar_2026-03-17.csv
```

---

## Données de démo incluses

| Fichier | Type | Contenu |
|---------|------|---------|
| `calendar/calendar_2026-03-17.csv` | Calendrier | 5 réunions le 17 mars 2026 |
| `calendar/calendar_2026-03-18.csv` | Calendrier | Réunions le 18 mars 2026 |
| `transcripts/acme_2026-03-10.txt` | Transcription | Sync produit Acme du 10 mars |
| `transcripts/carrefour_2026-02-25.txt` | Transcription | Point mensuel Carrefour |
| `transcripts/novatech_2026-03-05.txt` | Transcription | Découverte NovaTech |
| `summaries/acme_2026-03-10.csv` | Compte-rendu | Historique Acme avec actions OPEN |
| `summaries/carrefour_2026-02-25.csv` | Compte-rendu | Historique Carrefour avec actions OPEN |
| `summaries/novatech_2026-03-05.csv` | Compte-rendu | Actions post-découverte NovaTech |
| `notes/carrefour_2026-03-01.md` | Notes | Suivi intermédiaire Carrefour |
| `notes/acme_2026-02-17.md` | Notes | Notes détaillées réunion Acme |

---

## Dépannage

**"Aucune réunion trouvée"** : Vérifiez que votre fichier calendrier CSV a une colonne `date` au format `YYYY-MM-DD` et que la date correspond à votre requête.

**"Aucune donnée trouvée pour ce client"** : Vérifiez que le nom du client dans votre requête correspond au début du nom de fichier (ex: "carrefour" pour `carrefour_2026-02-25.csv`).

**Participants non reconnus** : Les participants externes doivent être au format `Prénom Nom (Société)` dans le CSV calendrier pour que l'historique soit chargé automatiquement.
