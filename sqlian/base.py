import six


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
