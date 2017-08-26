import numbers

import six

from .base import Named, Parsable, Sql, UnescapableError
from .utils import is_non_string_sequence, sql_format_string_literal


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
            return Sql(sql_format_string_literal(self.wrapped))
        raise UnescapableError(self.wrapped)

    @classmethod
    def parse_native(cls, value):
        if is_non_string_sequence(value):
            return List(*(cls.parse(v) for v in value))
        return super(Value, cls).parse_native(value)


class Composition(object):

    def __init__(self, *args):
        super(Composition, self).__init__()
        self.args = args

    def __repr__(self):
        return '{}({!r})'.format(
            type(self).__name__,
            ', '.join(repr(a) for a in self.args),
        )


class As(Composition):

    def __init__(self, expression, alias):
        super(As, self).__init__(expression, alias)
        self.expression = expression
        self.alias = alias

    def __sql__(self):
        return Sql('{} AS {}').format(self.expression, self.alias)


class Ordering(Composition):

    def __init__(self, expression, order):
        super(Ordering, self).__init__(expression, order)
        order = Sql(order.upper())
        if order not in ['ASC', 'DESC']:
            raise ValueError('unsupported ordering {!r}'.format(order))
        self.expression = expression
        self.order = order

    def __sql__(self):
        return Sql('{} {}').format(self.expression, self.order)


class List(Composition):

    def __init__(self, *children):
        super(List, self).__init__(*children)
        self.children = list(children)

    def __sql__(self):
        return Sql('({})').format(Sql(', ').join(self.children))


class Assign(Composition):

    def __init__(self, ref, value):
        super(Assign, self).__init__(ref, value)
        self.ref = ref
        self.value = value

    def __sql__(self):
        return Sql('{} = {}').format(self.ref, self.value)


ALLOWED_JOIN_TYPES = {
    '',
    'INNER',
    'LEFT',
    'LEFT OUTER',
    'RIGHT',
    'RIGHT OUTER',
    'FULL',
    'FULL OUTER',
    'CROSS',

    'NATURAL',
    'NATURAL INNER',
    'NATURAL LEFT',
    'NATURAL LEFT OUTER',
    'NATURAL RIGHT',
    'NATURAL RIGHT OUTER',
    'NATURAL FULL',
    'NATURAL FULL OUTER',
    'NATURAL CROSS',
}


class Join(Composition, Named):

    def __init__(self, item, join_type, join_item, on_using=None):
        super(Join, self).__init__(item, join_type, join_item, on_using)
        join_type = Sql(join_type.upper())
        if join_type not in ALLOWED_JOIN_TYPES:
            raise ValueError('unsupported join type {!r}'.format(join_type))
        self.item = item
        self.join_type = join_type
        self.join_item = join_item
        self.on_using = on_using

    def __sql__(self):
        parts = [self.item, self.join_type, self.sql_name, self.join_item]
        if self.on_using is not None:
            parts.append(self.on_using)
        return Sql(' ').join(parts)
