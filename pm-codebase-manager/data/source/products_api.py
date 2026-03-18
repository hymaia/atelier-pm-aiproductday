"""
products_api.py — Endpoints API pour la gestion des produits
Plateforme SaaS — API v2.3
"""

from typing import Optional
import time

# Constantes de configuration
BATCH_SIZE_LIMIT = 200          # Nombre max d'items par requête batch
RATE_LIMIT_PER_MINUTE = 1000    # Requêtes max par minute par tenant
BATCH_TIMEOUT_SECONDS = 30      # Timeout pour les requêtes batch


def get_product(tenant_id: str, product_id: str) -> dict:
    """
    Récupère un produit par son identifiant.
    
    Args:
        tenant_id: Identifiant du client (ex: "acme-corp")
        product_id: Identifiant unique du produit
    
    Returns:
        dict avec les champs: id, name, variants, price, stock, updated_at
    
    Raises:
        ProductNotFoundError: si le produit n'existe pas
        RateLimitError: si le tenant dépasse 1000 req/min
    """
    _check_rate_limit(tenant_id)
    return _fetch_from_db(tenant_id, product_id)


def get_products_batch(tenant_id: str, product_ids: list[str]) -> list[dict]:
    """
    Récupère plusieurs produits en une seule requête.
    
    IMPORTANT : Limite stricte à 200 items par appel.
    Au-delà, l'API retourne une erreur 422 (Unprocessable Entity).
    Pour de grands catalogues, fragmenter en lots de 200 maximum.
    
    Args:
        tenant_id: Identifiant du client
        product_ids: Liste d'IDs produits (max 200)
    
    Returns:
        Liste de produits dans le même ordre que product_ids.
        Si un produit n'existe pas, retourne None à sa position.
    
    Raises:
        BatchSizeLimitError: si len(product_ids) > 200
        TimeoutError: si la requête dépasse 30 secondes
    """
    if len(product_ids) > BATCH_SIZE_LIMIT:
        raise BatchSizeLimitError(
            f"Batch limité à {BATCH_SIZE_LIMIT} items. "
            f"Reçu : {len(product_ids)}. "
            f"Fragmenter en lots de {BATCH_SIZE_LIMIT} maximum."
        )

    _check_rate_limit(tenant_id)
    start = time.time()

    results = []
    for pid in product_ids:
        if time.time() - start > BATCH_TIMEOUT_SECONDS:
            raise TimeoutError(f"Batch timeout après {BATCH_TIMEOUT_SECONDS}s")
        try:
            results.append(_fetch_from_db(tenant_id, pid))
        except ProductNotFoundError:
            results.append(None)

    return results


def create_product_variant(tenant_id: str, product_id: str, variant: dict) -> dict:
    """
    Ajoute une variante à un produit existant.
    Feature ajoutée en v2.3 — disponible pour tous les tenants.
    
    Args:
        tenant_id: Identifiant du client
        product_id: Produit parent
        variant: dict avec les champs obligatoires:
            - sku (str): identifiant unique de la variante
            - attributes (dict): ex {"color": "red", "size": "M"}
            - price_override (float, optionnel): prix spécifique à cette variante
            - stock (int): quantité en stock
    
    Returns:
        Variante créée avec son id généré
    
    Raises:
        ProductNotFoundError: si le produit parent n'existe pas
        DuplicateSKUError: si le SKU existe déjà pour ce tenant
        ValidationError: si les champs obligatoires sont manquants
    """
    _check_rate_limit(tenant_id)
    _validate_variant(variant)
    return _save_variant(tenant_id, product_id, variant)


def _check_rate_limit(tenant_id: str) -> None:
    """Vérifie que le tenant ne dépasse pas 1000 req/min."""
    current_rate = _get_current_rate(tenant_id)
    if current_rate >= RATE_LIMIT_PER_MINUTE:
        raise RateLimitError(
            f"Rate limit atteint pour {tenant_id}: "
            f"{current_rate}/{RATE_LIMIT_PER_MINUTE} req/min. "
            f"Réessayer dans 60 secondes."
        )


# --- Exceptions ---

class ProductNotFoundError(Exception):
    pass

class BatchSizeLimitError(Exception):
    pass

class RateLimitError(Exception):
    pass

class DuplicateSKUError(Exception):
    pass

class ValidationError(Exception):
    pass
