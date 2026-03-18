# Changelog — v2.2.0

**Date de release** : 2026-02-03
**Sprint** : S-22
**Déployé par** : Équipe Platform

---

## Résumé

Release axée sur les performances et le cache des dashboards Carrefour Digital.
Réduction significative de la latence d'affichage des tableaux de bord en heures de pointe.

---

## Nouveautés

### Cache Redis pour les dashboards analytics (Carrefour Digital)
- **Avant** : chaque changement de page recalculait intégralement les données du dashboard (3-5s)
- **Après** : cache Redis avec TTL adaptatif (1 min pour les dashboards magasin, 10 min pour les globaux)
- **Stratégie stale-while-revalidate** : les données légèrement expirées sont servies pendant la revalidation
- **Invalidation ciblée** : `invalidate_store(store_id)` permet de forcer le rafraîchissement d'un magasin spécifique
- **Impact produit** : temps de chargement réduit de 3.8s → 0.4s en moyenne (-89%)

### Nouvelle API d'invalidation de cache
- `POST /cache/invalidate/store/{store_id}` — invalide le cache d'un magasin
- `POST /cache/invalidate/all` — vide tout le cache (usage restreint, admin seulement)
- **Dashboard ops** : nouvelles métriques `cache_hit_rate` et `cache_size_mb` dans le dashboard ops

---

## Corrections de bugs

- **[T-071]** Les dashboards globaux affichaient parfois des données du mauvais mois après minuit
- **[T-074]** Timeout 504 sur les dashboards avec plus de 500 magasins actifs
- **[T-078]** Les filtres de catégorie n'étaient pas pris en compte dans la clé de cache (données mélangées entre catégories)

---

## Changements techniques

- Ajout de `dashboard_cache.py` dans le service analytics
- Configuration Redis dédiée : `MAX_CACHE_SIZE_MB = 512`
- Monitoring : alertes PagerDuty si `cache_hit_rate < 70%` pendant 10 minutes consécutives

---

## Breaking changes

L'endpoint `GET /dashboards/{type}` retourne maintenant un header `X-Cache: HIT|MISS` pour faciliter le debug.
Non-breaking, mais à intégrer dans les outils de monitoring client.

---

## Migration

Aucune action requise.
Le cache est auto-initialisé au premier appel.
Redis doit être en version 6.0+ (déjà le cas en prod).
