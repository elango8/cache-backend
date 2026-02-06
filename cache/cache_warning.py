# cache/cache_warning.py
from typing import Dict


def cache_warning(source: str, timings_ms: Dict[str, float]) -> Dict[str, str]:
    """
    Adds cache-related warnings or diagnostics to API responses.
    """

    warning = {}

    if source == "db":
        warning["warning"] = "Cache miss – data served from database"

    if timings_ms:
        total = sum(timings_ms.values())
        if total > 500:
            warning["performance_warning"] = "High response latency detected"

    return warning
