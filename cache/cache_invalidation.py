import json
import logging
import threading
import time
from typing import Optional

CHANNEL = "cache_invalidation"
RECONNECT_DELAY = 5

logger = logging.getLogger(__name__)


def _deps():
    from cache.redis_cache1 import redis_client, delete_redis
    from cache.lru_cache import app_cache
    return redis_client, delete_redis, app_cache


class CacheInvalidationManager:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    # ---------- PUBLISH ----------
    def publish(self, key_prefix: str):
        redis_client, _, _ = _deps()
        if not redis_client:
            return

        redis_client.publish(
            CHANNEL,
            json.dumps({"key_prefix": key_prefix}),
        )

    # ---------- INVALIDATE ALL ----------
    def invalidate_all(self):
        """
        Invalidate all cache layers locally and broadcast to other nodes
        """
        _, delete_redis, app_cache = _deps()

        # Local clear
        app_cache.clear()
        delete_redis("")  # empty prefix = delete all Redis keys

        # Broadcast to other instances
        self.publish("")

    # ---------- LIFECYCLE ----------
    def start(self):
        with self._lock:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(
                target=self._listen_loop,
                daemon=True,
                name="cache-invalidation-listener",
            )
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False

    # ---------- LISTENER ----------
    def _listen_loop(self):
        while self._running:
            try:
                redis_client, _, _ = _deps()
                if not redis_client:
                    time.sleep(RECONNECT_DELAY)
                    continue

                pubsub = redis_client.pubsub()
                pubsub.subscribe(CHANNEL)

                for msg in pubsub.listen():
                    if not self._running:
                        break
                    if msg.get("type") == "message":
                        self._handle_message(msg)

            except Exception:
                logger.exception("Invalidation listener crashed")
                time.sleep(RECONNECT_DELAY)

    # ---------- HANDLE MESSAGE ----------
    def _handle_message(self, message: dict):
        try:
            _, delete_redis, app_cache = _deps()
            payload = json.loads(message["data"])
            prefix = payload.get("key_prefix")

            # Empty prefix = full clear
            if prefix == "":
                app_cache.clear()
                delete_redis("")
                return

            app_cache.invalidate_prefix(prefix)
            delete_redis(prefix)

        except Exception:
            logger.exception("Invalidation handling failed")


cache_invalidator = CacheInvalidationManager()
