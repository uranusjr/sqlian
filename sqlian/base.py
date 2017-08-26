import collections
import numbers
import re

import six

from . import utils


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
        if isinstance(other, collections.Mapping):
            other = {k: Value.parse(v).__sql__() for k, v in other.items()}
        elif isinstance(other, collections.Sequence):
            other = (Value.parse(v).__sql__() for v in other)
        else:
            other = Value.parse(other).__sql__()
        return type(self)(super(Sql, self) % other)

    def format(self, *args, **kwargs):
        args = (Value.parse(a).__sql__() for a in args)
        kwargs = {k: Value.parse(v).__sql__() for k, v in kwargs.items()}
        return type(self)(super(Sql, self).format(*args, **kwargs))

    def join(self, iterable):
        return type(self)(super(Sql, self).join(
            Value.parse(i).__sql__() for i in iterable
        ))


class UnescapableError(ValueError):
    def __init__(self, v):
        super(UnescapableError, self).__init__(
            '{} value {!r} cannot be escaped'.format(type(v).__name__, v),
        )


CAMEL_RE = re.compile(r'([a-z])([A-Z])')


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


class Parsable(object):
    """Mixin giving a class ability to handle native data.
    """
    @classmethod
    def parse_native(cls, value):
        """Provide basic handling for native value.

        The default implementation just wraps the value inside the class. You
        should generally override this method to provide better parsing, but
        almost never needs to call this (use ``parse()`` instead).
        """
        return cls(value)

    @classmethod
    def parse(cls, value):
        """Smart parsing interface.

        This pass native data to parse_native, and returns SQL constructs
        immediately to prevent re-parsing.
        """
        if hasattr(value, '__sql__'):
            return value
        return cls.parse_native(value)


class Value(Parsable):

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
