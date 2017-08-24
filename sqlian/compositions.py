from .base import Named, Sql


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

    def __new__(cls, *children):
        if len(children) == 1 and isinstance(children[0], cls):
            return children[0]  # Avoid wrapping a single List.
        return Composition.__new__(cls)

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


def parse_native_as_value_list(values):
    return List(*values)
