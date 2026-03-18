# Changelog — v2.3.0

**Date de release** : 2026-03-10
**Sprint** : S-24
**Déployé par** : Équipe Platform

---

## Résumé

Cette release se concentre sur la fiabilité des webhooks et la résilience de l'API batch.
Elle fait suite aux incidents de février (webhook timeouts chez NovaTech, batch failures chez Acme).

---

## Nouveautés

### Webhooks — Retry exponentiel + Dead Letter Queue (NovaTech)
- **Avant** : les webhooks échoués étaient abandonnés après 1 retry (délai fixe de 5s)
- **Après** : 5 retries avec backoff exponentiel (1s → 5s → 30s → 5min → 30min)
- **Dead Letter Queue** : après 5 échecs, l'événement est stocké en DLQ pour inspection manuelle
- **Nouveaux endpoints** :
  - `GET /webhooks/dead-letter` — liste les événements en DLQ
  - `POST /webhooks/dead-letter/{id}/retry` — rejoue un événement manuellement
- **Impact produit** : taux de livraison des webhooks estimé à 99.2% (vs 94.1% avant)

### API Batch — Validation et limites explicites (Acme Corp)
- **Avant** : les batches > 200 produits retournaient une erreur 500 générique
- **Après** : validation en entrée, erreur 422 explicite avec message `BATCH_SIZE_LIMIT exceeded`
- **Rate limiting** : `X-RateLimit-Remaining` et `X-RateLimit-Reset` ajoutés aux headers de réponse
- **Timeout** : `BATCH_TIMEOUT_SECONDS` porté à 30s (était 10s) pour les gros catalogues
- **Impact produit** : les clients API reçoivent maintenant des erreurs exploitables

---

## Corrections de bugs

- **[T-089]** Webhook signature HMAC incorrecte lorsque le payload contenait des caractères UTF-8 non-ASCII
- **[T-092]** `create_product_variant` retournait 200 même si le SKU parent n'existait pas → désormais 404
- **[T-095]** Fuite mémoire dans le batch processor pour les catalogues > 5 000 produits

---

## Changements techniques

- Migration de `webhook_handler.js` → `webhook_handler.ts` (TypeScript strict)
- Ajout de tests d'intégration pour les scénarios de retry (couverture 87%)
- Dépendance `node-fetch` remplacée par `fetch` natif (Node 18+)

---

## Breaking changes

Aucun breaking change dans cette version.

---

## Migration

Aucune action requise pour les clients existants.
Les nouveaux headers de rate limiting sont optionnels à consommer.
