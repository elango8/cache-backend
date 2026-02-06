import threading
import json
from cache.lru_cache import app_cache
from cache.redis_cache1 import delete_redis, redis_client

CHANNEL = "cache_invalidation"

def publish_invalidation(key_prefix: str):
    redis_client.publish(
        CHANNEL,
        json.dumps({"key_prefix": key_prefix})
    )

def listen_invalidation():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(CHANNEL)

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        payload = json.loads(message["data"])
        key_prefix = payload["key_prefix"]

        # 🔥 Invalidate Application-Level LRU
        app_cache.invalidate_prefix(key_prefix)

        # 🔥 Invalidate Redis keys
        delete_redis(key_prefix)

def start_pubsub_listener():
    thread = threading.Thread(
        target=listen_invalidation,
        daemon=True
    )
    thread.start()
