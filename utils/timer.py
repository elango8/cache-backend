import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed_ms = round((time.perf_counter() - self.start) * 1000, 3)
