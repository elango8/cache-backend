# main.py
import asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from products import search_products, get_product
from cache.cache_invalidation import cache_invalidator
from cache.cache_warning import cache_warning
from cache.warmup import cache_warmer
app = FastAPI(title="Multi-Layer Cache API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    cache_invalidator.start()
    asyncio.create_task(cache_warmer.warm())


@app.on_event("shutdown")
def shutdown():
    cache_invalidator.stop()


@app.get("/")
def root():
    return {"status": "API is running"}


@app.get("/search")
async def search(category: str):
    data, source, status, timings = await search_products(category)

    response = {
        "source": source,
        "timings_ms": timings,
        "count": len(data) if isinstance(data, list) else 0,
        "data": data,
    }

    response.update(cache_warning(source, timings))
    return response


@app.get("/product/{slug}")
async def product(slug: str):
    data, source, status, timings = await get_product(slug)

    if status == 404:
        raise HTTPException(status_code=404, detail="Product not found")

    response = {
        "source": source,
        "timings_ms": timings,
        "data": data,
    }

    response.update(cache_warning(source, timings))
    return response

@app.post("/cache/invalidate", status_code=status.HTTP_200_OK)
async def invalidate_cache():
    """
    Invalidate all cache layers (LRU + Redis)
    """
    cache_invalidator.invalidate_all()
    return {
        "status": "ok",
        "message": "All caches invalidated"
    }

@app.post("/cache/warm", status_code=status.HTTP_200_OK)
async def warm_cache():
    """
    Warm cache with predefined popular keys
    """
    await cache_warmer.warm()
    return {
        "status": "ok",
        "message": "Cache warmup triggered"
    }
