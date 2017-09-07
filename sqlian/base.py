import six

from .utils import is_non_string_sequence


class UnescapableError(ValueError):
    def __init__(self, v):
        super(UnescapableError, self).__init__(
            '{} value {!r} cannot be escaped'.format(type(v).__name__, v),
        )


class UnsupportedParameterError(ValueError):
    def __init__(self, value, what):
        super(UnsupportedParameterError, self).__init__(
            'unsupported {} {!r}'.format(what, value),
        )


class Sql(six.text_type):
    """A SQL string.
    """
    def __new__(cls, base=u''):
        return super(Sql, cls).__new__(cls, base)

    @classmethod
    def ensure(cls, value):
        if not isinstance(value, cls):
            raise UnescapableError(value)
        return value

    def __repr__(self):
        return 'Sql({})'.format(six.text_type.__repr__(self))

    def __sql__(self, engine):
        return self

    def __hash__(self):
        return six.text_type.__hash__(self)

    def __eq__(self, other):
        return isinstance(other, Sql) and super(Sql, self).__eq__(other)

    def format(self, *args, **kwargs):
        args = (self.ensure(a) for a in args)
        kwargs = {k: self.ensure(v) for k, v in kwargs.items()}
        return type(self)(super(Sql, self).format(*args, **kwargs))

    def join(self, iterable):
        return type(self)(super(Sql, self).join(
            self.ensure(x) for x in iterable
        ))


def is_single_row(iterable):
    return (
        getattr(iterable, '__single_row__', False) or
        any(not is_non_string_sequence(v) for v in iterable)
    )


class NativeRow(list):
    """A list that explicits represents a single row, not a sequence of rows.

    This acts like a normal list, but sets an explicit marker to indicate it
    is a single row, to disable the auto-parsing functionality.
    """
    __single_row__ = True


class Parsable(object):
    """Mixin giving a class ability to handle native data.
    """
    @classmethod
    def parse_native(cls, value, engine):
        """Provide basic handling for native value.

        The default implementation just wraps the value inside the class. You
        should generally override this method to provide better parsing, but
        almost never needs to call this (use ``parse()`` instead).
        """
        return cls(value)

    @classmethod
    def parse(cls, value, engine):
        """Smart parsing interface.

        This pass native data to parse_native, and returns SQL constructs
        immediately to prevent re-parsing.
        """
        if hasattr(value, '__sql__'):
            return value
        return cls.parse_native(value, engine)
