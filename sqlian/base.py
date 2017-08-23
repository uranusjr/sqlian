import functools
import numbers
import re

import six

from . import utils


CAMEL_RE = re.compile(r'([a-z])([A-Z])')


class Sql(six.text_type):
    """A SQL string.
    """
    def __new__(cls, base=u'', *args, **kwargs):
        if hasattr(base, '__sql__'):
            base = base.__sql__()
        return six.text_type.__new__(cls, base, *args, **kwargs)

    def __repr__(self):
        return 'Sql({})'.format(str.__repr__(self))

    def __sql__(self):
        return self

    def format(self, *args, **kwargs):
        args = (sql(a) for a in args)
        kwargs = {k: sql(v) for k, v in kwargs.items()}
        return type(self)(super(Sql, self).format(*args, **kwargs))

    def join(self, iterable):
        return type(self)(super(Sql, self).join(sql(i) for i in iterable))


class UnescapedError(TypeError):
    def __init__(self, v):
        super(UnescapedError, self).__init__('unescaped value {!r}'.format(v))


def assert_safe(f):
    """Make sure the decorated function returns an SQL object.
    """
    @functools.wraps(f)
    def safe_f(*args, **kwargs):
        v = f(*args, **kwargs)
        assert isinstance(v, Sql)
        return v

    return f


@assert_safe
def sql(obj):
    """Make an SQL string out of the input.
    """
    if hasattr(obj, '__sql__'):
        return obj.__sql__()
    if isinstance(obj, bool):
        return {True: Sql('TRUE'), False: Sql('FALSE')}[obj]
    if isinstance(obj, numbers.Number):
        return Sql(obj)
    if isinstance(obj, six.binary_type):
        obj = obj.decode('utf-8')
    if isinstance(obj, six.text_type):
        return Sql(utils.sql_format_string_literal(obj))
    raise UnescapedError(obj)


def class_name_to_sql_name(s):
    """Convert CamelCase name to ALL CAPS WITH SPACES.
    """
    return CAMEL_RE.sub(r'\1 \2', s).upper()


class Named(object):
    def __init__(self):
        self.type_name = type(self).__name__
        self.sql_name = Sql(getattr(
            type(self), 'sql_name',
            class_name_to_sql_name(self.type_name),
        ))
