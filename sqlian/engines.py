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

    return wrapped


class StandardEngine(object):
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
    def format_value(self, value):
        if value is None:
            return self.format_null()
        if value is star:
            return self.format_star()
        if isinstance(value, numbers.Number):
            return self.format_number(value)
        if isinstance(value, six.binary_type):
            return self.format_string(value.decode('utf-8'))
        if isinstance(value, six.text_type):
            return self.format_string(value)
        if hasattr(value, '__sql__'):
            return value.__sql__(self)
        raise UnescapableError(value)

    def format_identifier(self, name):
        # TODO: Escape special characters?
        return '"{}"'.format(name)
