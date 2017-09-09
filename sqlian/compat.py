import contextlib
import functools
import sys


try:
    lru_cache = functools.lru_cache
except AttributeError:
    # Fake, doesn't cache.
    # TODO: Maybe use backports.functools_lru_cache when it's available?
    def lru_cache(*args, **kwargs):
        def decorator(f):
            return f
        return decorator


try:
    suppress = contextlib.suppress
except AttributeError:
    # Equivalent implementation as specified in docs.
    class suppress(object):
        def __init__(self, *excs): self._excs = excs    # noqa
        def __enter__(self): pass   # noqa
        def __exit__(self, exctype, excinst, exctb):    # noqa
            return exctype is not None and issubclass(exctype, self._excs)


if sys.version_info >= (3, 2):
    update_wrapper = functools.update_wrapper
else:
    # Provide __wrapped__ attribute.
    def update_wrapper(wrapper, wrapped, *args, **kwargs):
        functools.update_wrapper(wrapper, wrapped, *args, **kwargs)
        wrapper.__wrapped__ = wrapped
        return wrapper
