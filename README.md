# PM Meeting Assistant

Outil de démonstration pour Product Managers. Déposez vos fichiers de données de réunions et obtenez en langage naturel :

1. **Briefing du matin** — Agenda du jour avec contexte de chaque réunion
2. **Préparation de réunion** — Historique, participants, last touchpoint

Propulsé par **Claude Opus 4.6** (Anthropic).

---

## Structure du projet

```
pm-meeting-assistant/
├── data/
│   ├── calendar/          # .ics ou CSV agenda
│   ├── transcripts/       # Transcriptions .txt ou .json
│   ├── notes/             # Notes .md, .pdf, .docx
│   └── summaries/         # Comptes-rendus CSV (date, participants, décisions, actions)
├── skills/
│   ├── morning_briefing.py
│   └── prepare_meeting.py
├── loaders/
│   ├── calendar_loader.py
│   ├── transcript_loader.py
│   ├── notes_loader.py
│   └── summary_loader.py
├── indexer.py
├── index.json             # Généré automatiquement
├── main.py
└── requirements.txt
```

---

## Installation

```bash
# 1. Cloner / copier le projet
cd pm-meeting-assistant

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Utilisation

### Lancement principal (recommandé)

```bash
python main.py
```

Le programme :
1. Détecte et indexe automatiquement les nouveaux fichiers dans `data/`
2. Affiche le résumé de l'index
3. Propose le menu des deux skills

### Indexer manuellement

```bash
# Indexer les nouveaux fichiers
python indexer.py

# Reconstruire l'index depuis zéro
python indexer.py --reset
```

### Lancer les skills directement

```bash
# Briefing du matin (aujourd'hui)
python skills/morning_briefing.py

# Briefing pour une date précise
python skills/morning_briefing.py 2026-03-17

# Préparer une réunion
python skills/prepare_meeting.py "Acme Corp"
python skills/prepare_meeting.py "Julie Chen"
python skills/prepare_meeting.py "NovaTech"
```

---

## Format des fichiers de données

### Calendrier CSV (`data/calendar/`)

```csv
date,start_time,end_time,title,participants,location,description
2026-03-17,09:00,09:45,Sync produit Acme,Alice;Bob;Sarah (Acme),Zoom,Point hebdomadaire
```

### Transcription TXT (`data/transcripts/`)

```
Date: 2026-03-10
Titre: Sync produit Acme Corp
Participants: Alice Martin, Bob Leroy, Sarah Kim (Acme)

[Contenu de la transcription...]

Actions pour la semaine :
- James : ajuster l'implémentation batch
- Alice : envoyer les release notes
```

### Compte-rendu CSV (`data/summaries/`)

```csv
date,participants,title,decisions,actions,status
2026-03-10,"Alice, Bob, Sarah",Sync Acme,"Décision 1; Décision 2","Alice : préparer doc [OPEN]; Bob : envoyer email [DONE]",done
```

**Important** : Les actions non résolues doivent contenir `[OPEN]` pour être détectées.

### Notes Markdown (`data/notes/`)

Format Notion export ou markdown standard :

```markdown
# Titre de la réunion
**Date :** 1er mars 2026
**Participants :** Alice Martin, Marc Dupont

## Décisions
- Décision 1
- Décision 2

## Actions
- [ ] Alice : préparer le deck
- [x] Marc : envoyer les métriques
```

---

## Convention de nommage des fichiers

Pour une extraction automatique des métadonnées, nommez vos fichiers :

```
{client}_{YYYY-MM-DD}.{ext}

Exemples :
  acme_2026-03-10.txt
  carrefour_2026-02-25.csv
  novatech_2026-03-05.txt
  calendar_2026-03-17.csv
```

---

## Architecture technique

### Indexer (index.json)

L'indexer scanne `data/` et extrait les métadonnées **sans lire le contenu complet** des fichiers. L'index JSON résultant est léger (quelques Ko) et rapide à charger.

```json
[
  {
    "id": "abc123",
    "path": "data/transcripts/acme_2026-03-10.txt",
    "type": "transcript",
    "date": "2026-03-10",
    "client": "Acme",
    "participants": ["Alice Martin", "Bob Leroy"],
    "title": "Sync produit Acme Corp",
    "size_kb": 2.1,
    "indexed_at": "2026-03-17T08:00:00"
  }
]
```

### Pattern de retrieval en deux étapes

Les deux skills suivent le même pattern pour passer à l'échelle :

**Étape 1 — Filtrage sur index.json** (jamais de lecture de fichiers)
- Charger `index.json` (quelques Ko)
- Filtrer sur date, client, participants
- Identifier les fichiers pertinents

**Étape 2 — Lecture ciblée** (max 10 fichiers)
- Charger uniquement les fichiers identifiés via les loaders
- Passer le contenu à Claude pour génération

---

## Données de démo incluses

| Fichier | Type | Contenu |
|---------|------|---------|
| `calendar/calendar_2026-03-17.csv` | Calendrier | 5 réunions le 17 mars 2026 |
| `transcripts/acme_2026-03-10.txt` | Transcription | Sync produit Acme du 10 mars |
| `transcripts/carrefour_2026-02-25.txt` | Transcription | Point mensuel Carrefour |
| `transcripts/novatech_2026-03-05.txt` | Transcription | Découverte NovaTech |
| `summaries/acme_2026-03-10.csv` | Compte-rendu | Historique Acme avec actions OPEN |
| `summaries/carrefour_2026-02-25.csv` | Compte-rendu | Historique Carrefour avec actions OPEN |
| `summaries/novatech_2026-03-05.csv` | Compte-rendu | Actions post-découverte NovaTech |
| `notes/carrefour_2026-03-01.md` | Notes | Suivi intermédiaire Carrefour |
| `notes/acme_2026-02-17.md` | Notes | Notes détaillées réunion Acme |

---

## Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `ANTHROPIC_API_KEY` | Clé API Anthropic | Oui |

---

## Dépannage

**"Index vide"** : Lancez `python indexer.py` depuis le répertoire du projet.

**"Aucune réunion trouvée"** : Vérifiez que votre fichier calendrier CSV a une colonne `date` au format `YYYY-MM-DD` et que la date correspond.

**Erreur PDF/DOCX** : Vérifiez que `pdfplumber` et `python-docx` sont installés.

**Réponses lentes** : Normal — Claude Opus 4.6 avec adaptive thinking peut prendre 10-30s pour les requêtes complexes.
