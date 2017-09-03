import six


class UnescapableError(ValueError):
    def __init__(self, v):
        super(UnescapableError, self).__init__(
            '{} value {!r} cannot be escaped'.format(type(v).__name__, v),
        )


class Sql(six.text_type):
    """A SQL string.
    """
    def __repr__(self):
        return 'Sql({})'.format(six.text_type.__repr__(self))

    def __sql__(self, engine):
        return self

    def __eq__(self, other):
        return isinstance(other, Sql) and super(Sql, self).__eq__(other)

    def join(self, iterable):
        return type(self)(super(Sql, self).join(Sql(x) for x in iterable))
