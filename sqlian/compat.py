import functools


try:
    lru_cache = functools.lru_cache
except AttributeError:
    def lru_cache(*args, **kwargs):  # Fake, doesn't cache.
        def decorator(f):
            return f
        return decorator
