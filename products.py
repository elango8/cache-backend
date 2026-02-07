from cache.cache_manager import cached_search, cached_product


async def search_products(category: str):
    data, source, timings = await cached_search(category)
    return data, source, 200, timings


async def get_product(slug: str):
    data, source, timings = await cached_product(slug)

    if source == "not_found":
        return None, source, 404, timings

    return data, source, 200, timings