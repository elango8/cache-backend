import asyncio
import logging
from typing import List

from db import get_db
from cache.lru_cache import app_cache
from cache.redis_cache1 import set_redis
from cache.cache_coherence import product_key, search_key

logger = logging.getLogger(__name__)


class CacheWarmer:
    def __init__(self, limit_per_category: int = 20):
        self.limit = limit_per_category

    async def warm(self):
        try:
            categories = await self._get_active_categories()
            await asyncio.gather(
                *[self._warm_category(c) for c in categories]
            )
        except Exception:
            logger.exception("Cache warm failed (non-fatal)")

    async def _get_active_categories(self) -> List[str]:
        return await get_db().products.distinct(
            "category", {"isActive": True}
        )

    async def _warm_category(self, category: str):
        cursor = (
            get_db().products
            .find({"category": category, "isActive": True})
            .limit(self.limit)
        )

        products = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            products.append(doc)

        if not products:
            return

        s_key = search_key(category)
        set_redis(s_key, products)
        app_cache.put(s_key, products)

        for p in products:
            p_key = product_key(p["slug"])
            set_redis(p_key, p)
            app_cache.put(p_key, p)


cache_warmer = CacheWarmer()
