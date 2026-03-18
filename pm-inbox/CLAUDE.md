# pm-inbox — Gestion des messages entrants

## Périmètre
- Lecture des nouveaux emails et messages Slack
- Triage par urgence et type d'action requise
- Génération de brouillons de réponse dans le ton du PM

## Skills disponibles

### triage-inbox
Lit tous les messages en attente (emails + Slack) et les classe par urgence.
Invoquer quand l'utilisateur demande : ses messages non lus, ce qui l'attend, les urgences du jour.

### draft-reply
Génère un brouillon de réponse pour un expéditeur ou sujet précis.
Invoquer quand l'utilisateur veut répondre à un message spécifique.
Argument : nom de l'expéditeur ou mot-clé du sujet.

## Règle — Profil PM
Pour draft-reply, injecter `context/pm_profile.md` (à la racine du workspace) afin d'écrire dans le ton du PM.
Le profil est injecté via `!`cat "${CLAUDE_SKILL_DIR}/../../../../context/pm_profile.md"`` dans le SKILL.md.

## RÈGLE ABSOLUE — Anti-hallucination
Ne jamais inventer de messages ou d'informations absents des fichiers data/.
Si aucun message trouvé : répondre exactement "AUCUN MESSAGE EN ATTENTE" sans inventer.
Toujours indiquer la source consultée (emails/ ou slack/).

## Architecture
```
pm-inbox/
├── data/
│   ├── emails/        ← fichiers .md (From, Subject, Date, body)
│   └── slack/         ← fichiers .md (Channel, From, Timestamp, body)
├── utils/
│   ├── email_loader.py
│   └── slack_loader.py
└── .claude/skills/
    ├── triage-inbox/
    │   ├── SKILL.md
    │   └── fetch_messages.py
    └── draft-reply/
        ├── SKILL.md
        └── fetch_message.py
```
