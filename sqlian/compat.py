import functools


try:
    lru_cache = functools.lru_cache
except AttributeError:
    # Fake, doesn't cache.
    # TODO: Maybe use backports.functools_lru_cache when it's available?
    def lru_cache(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
