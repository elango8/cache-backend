from utils.timer import Timer
from cache.lru_cache import app_cache
from cache.redis_cache1 import get_redis, set_redis
from db import get_db
from pymongo.errors import PyMongoError


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def finalize_timings(timings: dict):
    timings["total"] = sum(
        v for v in timings.values()
        if isinstance(v, (int, float))
    )
    return timings

async def cached_search(category: str):
    key = f"search:{category}"
    timings = {}

    with Timer() as t:
        data = app_cache.get(key)
    timings["lru_ms"] = t.elapsed_ms
    if data is not None:
        return data, "lru_cache", finalize_timings(timings)

    with Timer() as t:
        data = get_redis(key)
    timings["redis_ms"] = t.elapsed_ms
    if data is not None:
        app_cache.put(key, data)
        return data, "redis", finalize_timings(timings)

    try:
        with Timer() as t:
            cursor = get_db().products.find(
                {"category": category, "isActive": True}
            )
            data = [serialize(doc) async for doc in cursor]
        timings["db_ms"] = t.elapsed_ms

        if data:
            set_redis(key, data)
            app_cache.put(key, data)

        return data, "db", finalize_timings(timings)

    except PyMongoError as e:
        timings["error"] = str(e)
        return [], "db_error", finalize_timings(timings)

async def cached_product(slug: str):
    key = f"product:{slug}"
    timings = {}

    with Timer() as t:
        data = app_cache.get(key)
    timings["lru_ms"] = t.elapsed_ms
    if data is not None:
        return data, "lru_cache", finalize_timings(timings)

    with Timer() as t:
        data = get_redis(key)
    timings["redis_ms"] = t.elapsed_ms
    if data is not None:
        app_cache.put(key, data)
        return data, "redis", finalize_timings(timings)

    try:
        with Timer() as t:
            doc = await get_db().products.find_one({"slug": slug})
        timings["db_ms"] = t.elapsed_ms

        if not doc:
            return None, "not_found", finalize_timings(timings)

        data = serialize(doc)
        set_redis(key, data)
        app_cache.put(key, data)

        return data, "db", finalize_timings(timings)

    except Exception as e:
        timings["error"] = str(e)
        return None, "db_error", finalize_timings(timings)
