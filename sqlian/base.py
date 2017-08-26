import functools
import numbers
import re

import six

from . import utils


CAMEL_RE = re.compile(r'([a-z])([A-Z])')


def assert_sql(f):
    """Make sure the decorated function returns an SQL object.
    """
    @functools.wraps(f)
    def safe_f(*args, **kwargs):
        v = f(*args, **kwargs)
        assert isinstance(v, Sql)
        return v

    return f


class Sql(six.text_type):
    """A SQL string.
    """
    def __new__(cls, base=u'', *args, **kwargs):
        if hasattr(base, '__sql__'):
            base = base.__sql__()
        return six.text_type.__new__(cls, base, *args, **kwargs)

    def __repr__(self):
        return 'Sql({})'.format(six.text_type.__repr__(self))

    def __sql__(self):
        return self

    def __mod__(self, other):
        return type(self)(super(Sql, self) % sql(other))

    def format(self, *args, **kwargs):
        args = (sql(a) for a in args)
        kwargs = {k: sql(v) for k, v in kwargs.items()}
        return type(self)(super(Sql, self).format(*args, **kwargs))

    def join(self, iterable):
        return type(self)(super(Sql, self).join(sql(i) for i in iterable))


class UnescapableError(ValueError):
    def __init__(self, v):
        super(UnescapableError, self).__init__(
            '{} value {!r} cannot be escaped'.format(type(v).__name__, v),
        )


@assert_sql
def sql(obj):
    if hasattr(obj, '__sql__'):
        return obj.__sql__()
    raise UnescapableError(obj)


def class_name_to_sql_name(s):
    """Convert CamelCase name to ALL CAPS WITH SPACES.
    """
    return CAMEL_RE.sub(r'\1 \2', s).upper()


class Named(object):
    """Mixin class providing SQL information via introspection.
    """
    def __init__(self):
        self.type_name = type(self).__name__
        self.sql_name = Sql(getattr(
            type(self), 'sql_name',
            class_name_to_sql_name(self.type_name),
        ))


class Value(object):

    __slots__ = ('wrapped',)

    def __init__(self, wrapped):
        super(Value, self).__init__()
        self.wrapped = wrapped

    def __repr__(self):
        return 'Value({!r})'.format(self.wrapped)

    def __sql__(self):
        if self.wrapped is None:
            return Sql('NULL')
        if isinstance(self.wrapped, bool):
            return {True: Sql('TRUE'), False: Sql('FALSE')}[self.wrapped]
        if isinstance(self.wrapped, numbers.Number):
            return Sql(self.wrapped)
        if isinstance(self.wrapped, six.binary_type):
            self.wrapped = self.wrapped.decode('utf-8')
        if isinstance(self.wrapped, six.text_type):
            return Sql(utils.sql_format_string_literal(self.wrapped))
        raise UnescapableError(self.wrapped)
