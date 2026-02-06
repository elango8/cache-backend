"""
Cache Coherence Rules
--------------------
MongoDB = source of truth
Redis   = shared cache (cross-process)
LRU     = per-process cache (in-memory)

RULES:
1. Reads never mutate the database
2. Writes MUST invalidate related cache keys
3. Cache is rebuilt lazily on subsequent reads
"""

from typing import List


# ======================================================
# CACHE KEY DEFINITIONS
# ======================================================

def product_key(slug: str) -> str:
    """
    Cache key for a single product.
    """
    return f"product:{slug}"


def search_key(category: str) -> str:
    """
    Cache key for product search by category.
    """
    return f"search:{category}"


# ======================================================
# INVALIDATION RULES
# ======================================================

def invalidation_keys_for_product(
    slug: str,
    category: str
) -> List[str]:
    """
    When a product is created / updated / deleted,
    the following cache keys become stale.
    """
    return [
        product_key(slug),
        search_key(category),
    ]
