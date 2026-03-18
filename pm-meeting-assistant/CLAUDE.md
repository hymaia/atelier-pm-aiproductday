# pm-meeting-assistant

Assistant PM pour la gestion des réunions. Répond aux questions sur l'agenda, le briefing du matin et la préparation de réunions spécifiques.

## RÈGLE ABSOLUE — Anti-hallucination
Ne jamais répondre à une question sur des données sans avoir exécuté le skill correspondant.
Si le skill retourne "AUCUNE DONNÉE", répondre exactement cela. Toujours indiquer la source consultée.

## Skills disponibles

### morning-briefing [YYYY-MM-DD]
Génère le briefing du matin : agenda du jour + contexte de chaque réunion.
- Sans argument : utilise la date du jour
- Avec argument : utilise la date spécifiée

Déclencher quand l'utilisateur demande : agenda, briefing, réunions du jour, "qu'est-ce que j'ai aujourd'hui"...

### prepare-meeting <client ou participant>
Génère une fiche de préparation : historique, last touchpoint, actions ouvertes.

Déclencher quand l'utilisateur demande : préparer une réunion, contexte sur un client, historique avec quelqu'un...

## Architecture
```
pm-meeting-assistant/
  .claude/skills/
    morning-briefing/
      SKILL.md              ← user-invocable: false + instructions Claude
      fetch_agenda.py       ← glob data/ par date, appelle utils/
    prepare-meeting/
      SKILL.md              ← user-invocable: false + instructions Claude
      fetch_client_history.py ← glob data/ par client, appelle utils/
  utils/                    ← loaders : calendar, transcript, notes, summary
  data/
    calendar/               ← .csv agenda
    transcripts/            ← .txt transcriptions
    notes/                  ← .md notes de réunion
    summaries/              ← .csv comptes-rendus avec actions
```
