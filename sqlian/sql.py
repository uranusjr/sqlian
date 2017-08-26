import functools

from . import queries as q
from .base import Sql, UnescapableError


def assert_sql(f):
    """Make sure the decorated function returns an SQL object.
    """
    @functools.wraps(f)
    def safe_f(*args, **kwargs):
        v = f(*args, **kwargs)
        assert isinstance(v, Sql)
        return v

    return f


@assert_sql
def sql(obj):
    if hasattr(obj, '__sql__'):
        return obj.__sql__()
    raise UnescapableError(obj)


def select(*args, **kwargs):
    return sql(q.Select(*args, **kwargs))


def insert(*args, **kwargs):
    return sql(q.Insert(*args, **kwargs))


def update(*args, **kwargs):
    return sql(q.Update(*args, **kwargs))


def delete(*args, **kwargs):
    return sql(q.Delete(*args, **kwargs))
