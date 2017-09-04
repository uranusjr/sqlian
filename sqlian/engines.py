import functools
import numbers

import six

from .base import Sql, UnescapableError
from .constants import star


def ensure_sql(f):

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        result = f(*args, **kwargs)
        return result if isinstance(result, Sql) else Sql(result)

    wrapped.__sql_ensured__ = True
    return wrapped


class EngineMeta(type):
    """Metaclass to ensure ``as_sql`` returns a ``Sql`` instance.
    """
    def __new__(meta, name, bases, attrdict):
        if 'as_sql' in attrdict:
            as_sql = attrdict['as_sql']
            if not getattr(as_sql, '__sql_ensured__', False):
                attrdict['as_sql'] = ensure_sql(as_sql)
        return super(EngineMeta, meta).__new__(meta, name, bases, attrdict)


@six.add_metaclass(EngineMeta)
class Engine(object):
    """An engine that does nothing.
    """


class StandardEngine(Engine):
    """Engine that emits ANSI-compliant SQL.
    """
    def format_star(self):
        return '*'

    def format_null(self):
        return 'NULL'

    def format_number(self, value):
        return str(value)

    def format_string(self, value):
        # SQL standard: replace single quotes with pairs of them.
        value = value.replace("'", "''")
        if '\0' in value:   # TODO: Is there a good way to handle this?
            raise ValueError('null character in string')
        return "'{}'".format(value)

    @ensure_sql
    def as_sql(self, value):
        if value is None:
            return self.format_null()
        if value is star:
            return self.format_star()
        if hasattr(value, '__sql__'):
            return value.__sql__(self)
        if isinstance(value, numbers.Number):
            return self.format_number(value)
        if isinstance(value, six.binary_type):
            return self.format_string(value.decode('utf-8'))
        if isinstance(value, six.text_type):
            return self.format_string(value)

        raise UnescapableError(value)

    def format_identifier(self, name):
        # TODO: Escape special characters?
        return '"{}"'.format(name)
