# cache/write_through.py
from cache.redis_cache1 import set_redis
from cache.cache_invalidation import cache_invalidator

DEFAULT_TTL = 60


def write_through_product(product: dict):
    """
    Write-through cache for single product update.
    """
    product_id = str(product["_id"])

    # 1️⃣ Update product cache
    set_redis(
        key=f"product:{product_id}",
        value=product,
        ttl=DEFAULT_TTL,
    )

    # 2️⃣ Invalidate dependent caches
    category = product.get("category")
    if category:
        cache_invalidator.publish(f"search:{category}")
