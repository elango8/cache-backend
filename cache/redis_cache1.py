# cache/redis_cache1.py
import redis
import json
import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ---------- REDIS CLIENT ----------
try:
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )
    redis_client.ping()
except Exception as e:
    logger.error("Redis unavailable, continuing without Redis", exc_info=e)
    redis_client = None


# ---------- JSON SERIALIZER ----------
def json_serializer(obj):
    """
    Converts non-JSON-safe objects to JSON-safe formats.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not JSON serializable")


# ---------- READ ----------
def get_redis(key: str) -> Optional[Any]:
    """
    Safe Redis GET.
    Returns None if Redis is down or key not found.
    """
    if not redis_client:
        return None

    try:
        value = redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception:
        logger.exception("Redis GET failed")
        return None


# ---------- WRITE ----------
def set_redis(key: str, value: Any, ttl: int = 60):
    """
    Safe Redis SET with TTL.
    Handles datetime serialization.
    """
    if not redis_client:
        return

    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=json_serializer)
        )
    except Exception:
        logger.exception("Redis SET failed")


# ---------- INVALIDATION ----------
def delete_redis(prefix: str):
    """
    Delete keys by prefix (used by invalidation).
    """
    if not redis_client:
        return

    try:
        keys = redis_client.keys(f"{prefix}*")
        if keys:
            redis_client.delete(*keys)
    except Exception:
        logger.exception("Redis delete failed")
