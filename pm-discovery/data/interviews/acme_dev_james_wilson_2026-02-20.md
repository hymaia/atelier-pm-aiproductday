---
date: 2026-02-20
persona: Développeur Intégrateur
client: Acme Corp
interviewer: Bob Leroy
duration: 45min
themes: [api, documentation, developer-experience]
---

# Interview — James Wilson, Lead Dev Acme Corp

**Contexte :** Référent technique de l'intégration API chez Acme. Travaille sur le projet depuis janvier. Responsable de l'implémentation batch et webhooks.

---

## Verbatims clés

**Sur l'expérience développeur :**
> "La doc est bien pour les cas simples. Dès que tu sors du happy path, tu es seul. J'ai passé 2 jours à comprendre le comportement du endpoint batch quand le payload est supérieur à 500 items — ce n'est nulle part dans la doc."

> "Le SDK Python est propre. Bien typé, les erreurs sont explicites. Je préfère ça à devoir faire les appels REST à la main."

**Sur les limites de l'API :**
> "J'ai découvert la limite de rate limiting en production. Pas en dev, en production. C'est le genre de chose qui doit être dans un encart rouge en haut de la doc."

> "Le endpoint `/products/batch` timeout à partir de 500 items. On a dû refactorer notre pipeline d'import. Ça nous a coûté une semaine."

**Sur le support :**
> "Bob est réactif, ça aide. Mais j'aimerais un canal Slack dédié ou un forum où les devs partagent leurs solutions. En ce moment je cherche dans GitHub Issues et c'est le désert."

## Pain points identifiés
1. Documentation incomplète sur les cas limites (rate limiting, batch, pagination)
2. Découverte des limites en production plutôt qu'en développement
3. Pas de communauté développeurs / forum d'entraide
4. Onboarding technique trop long pour une intégration qui devrait être simple

## Ce qui fonctionne
- SDK Python de qualité
- Support direct réactif (Bob Leroy)
- Environnement de test dédié disponible
