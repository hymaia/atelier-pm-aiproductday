"""
dashboard_cache.py — Carrefour Digital
Couche de cache pour les dashboards analytiques.

Problème résolu : les dashboards analytics se rechargent à chaque page change,
causant 3-5s de latence et des timeouts en pic de trafic.
Solution : cache Redis avec TTL configurable + invalidation sélective par store_id.
"""
from __future__ import annotations

import time
import hashlib
import json
from typing import Any

# Configuration du cache
DEFAULT_TTL_SECONDS = 300          # 5 minutes par défaut
STORE_DASHBOARD_TTL = 60           # 1 minute pour les dashboards magasin (données plus dynamiques)
GLOBAL_DASHBOARD_TTL = 600         # 10 minutes pour les dashboards globaux
MAX_CACHE_SIZE_MB = 512            # Limite mémoire Redis allouée aux dashboards
STALE_WHILE_REVALIDATE_SECONDS = 30  # Sert le cache expiré pendant ce délai pendant la revalidation


class CacheMissError(Exception):
    """Aucune entrée en cache pour cette clé."""
    pass


class CacheFullError(Exception):
    """Le cache a atteint sa limite MAX_CACHE_SIZE_MB."""
    pass


class StaleDataWarning(UserWarning):
    """Les données servies sont expirées mais la revalidation est en cours."""
    pass


def _build_cache_key(dashboard_type: str, filters: dict) -> str:
    """
    Construit une clé de cache déterministe à partir du type de dashboard et des filtres.

    Args:
        dashboard_type: ex. "store_performance", "category_sales", "global_kpis"
        filters: dict de filtres appliqués (store_id, date_range, category...)

    Returns:
        Clé de cache SHA-256 préfixée par dashboard_type.
    """
    filters_hash = hashlib.sha256(
        json.dumps(filters, sort_keys=True).encode()
    ).hexdigest()[:16]
    return f"dashboard:{dashboard_type}:{filters_hash}"


def get_dashboard(dashboard_type: str, filters: dict, redis_client: Any) -> dict:
    """
    Récupère un dashboard depuis le cache Redis.

    Stratégie stale-while-revalidate :
    - Si le cache est valide → retourne immédiatement
    - Si le cache est expiré depuis moins de STALE_WHILE_REVALIDATE_SECONDS → retourne les données périmées
      et déclenche une revalidation asynchrone en arrière-plan
    - Si le cache est absent ou trop ancien → lève CacheMissError

    Args:
        dashboard_type: Type de dashboard à récupérer.
        filters: Filtres appliqués (ex. {"store_id": "42", "date": "2026-03"}).
        redis_client: Instance Redis connectée.

    Returns:
        dict avec "data" (contenu du dashboard) et "cached_at" (timestamp).

    Raises:
        CacheMissError: Si aucune donnée valide n'est disponible.
    """
    key = _build_cache_key(dashboard_type, filters)
    raw = redis_client.get(key)

    if raw is None:
        raise CacheMissError(f"No cache entry for key: {key}")

    entry = json.loads(raw)
    age = time.time() - entry["cached_at"]
    ttl = STORE_DASHBOARD_TTL if "store_id" in filters else GLOBAL_DASHBOARD_TTL

    if age > ttl + STALE_WHILE_REVALIDATE_SECONDS:
        raise CacheMissError(f"Cache entry too stale ({age:.0f}s > {ttl + STALE_WHILE_REVALIDATE_SECONDS}s)")

    if age > ttl:
        import warnings
        warnings.warn(
            f"Serving stale data for {key} ({age:.0f}s old). Revalidation in progress.",
            StaleDataWarning,
        )

    return entry


def set_dashboard(dashboard_type: str, filters: dict, data: dict, redis_client: Any) -> str:
    """
    Stocke un dashboard dans le cache Redis.

    Args:
        dashboard_type: Type de dashboard.
        filters: Filtres appliqués (utilisés pour construire la clé).
        data: Données du dashboard à mettre en cache.
        redis_client: Instance Redis connectée.

    Returns:
        La clé de cache utilisée.

    Raises:
        CacheFullError: Si Redis a atteint MAX_CACHE_SIZE_MB.
    """
    # Vérification de la mémoire disponible
    info = redis_client.info("memory")
    used_mb = info["used_memory"] / (1024 * 1024)
    if used_mb > MAX_CACHE_SIZE_MB:
        raise CacheFullError(
            f"Redis cache full: {used_mb:.1f}MB used / {MAX_CACHE_SIZE_MB}MB max"
        )

    key = _build_cache_key(dashboard_type, filters)
    ttl = STORE_DASHBOARD_TTL if "store_id" in filters else GLOBAL_DASHBOARD_TTL

    entry = {
        "data": data,
        "cached_at": time.time(),
        "dashboard_type": dashboard_type,
        "filters": filters,
    }
    redis_client.setex(key, ttl + STALE_WHILE_REVALIDATE_SECONDS, json.dumps(entry))
    return key


def invalidate_store(store_id: str, redis_client: Any) -> int:
    """
    Invalide toutes les entrées de cache liées à un magasin spécifique.
    Utilisé lors d'une mise à jour de données en temps réel (ex: clôture de journée).

    Args:
        store_id: Identifiant du magasin (ex. "42").
        redis_client: Instance Redis connectée.

    Returns:
        Nombre de clés supprimées.
    """
    pattern = f"dashboard:store_performance:*"
    keys = redis_client.keys(pattern)
    deleted = 0
    for key in keys:
        raw = redis_client.get(key)
        if raw:
            entry = json.loads(raw)
            if entry.get("filters", {}).get("store_id") == store_id:
                redis_client.delete(key)
                deleted += 1
    return deleted


def invalidate_all_dashboards(redis_client: Any) -> int:
    """
    Vide intégralement le cache des dashboards. À n'utiliser qu'en cas de déploiement
    ou de migration de données.

    Args:
        redis_client: Instance Redis connectée.

    Returns:
        Nombre de clés supprimées.
    """
    keys = redis_client.keys("dashboard:*")
    if keys:
        return redis_client.delete(*keys)
    return 0
