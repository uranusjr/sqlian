from sqlian import Sql, UnsupportedParameterError


__all__ = [
    'Composition',
    'As', 'Assign', 'Join', 'List', 'Ordering',
]


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

    def __sql__(self, engine):
        return Sql('{} AS {}').format(
            engine.as_value(self.expression),
            engine.as_value(self.alias),
        )


class Ordering(Composition):

    allowed_orderings = ['ASC', 'DESC']

    def __init__(self, expression, order):
        order_upper = order.upper()
        super(Ordering, self).__init__(expression, order_upper)
        if order_upper not in self.allowed_orderings:
            raise UnsupportedParameterError(order, 'ordering')
        self.expression = expression
        self.order = order_upper

    def __sql__(self, engine):
        return Sql('{} {}').format(
            engine.as_value(self.expression),
            Sql(self.order),
        )


class List(Composition):
    def __sql__(self, engine):
        return Sql('({})').format(Sql(', ').join(
            engine.as_value(a) for a in self.args
        ))


class Assign(Composition):

    def __init__(self, lho, rho):
        super(Assign, self).__init__(lho, rho)
        self.lho = lho
        self.rho = rho

    def __sql__(self, engine):
        return Sql('{} = {}').format(
            engine.as_value(self.lho),
            engine.as_value(self.rho),
        )


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


class Join(Composition):

    sql_name = 'JOIN'

    def __init__(self, item, join_type, join_item, on_using=None):
        join_type_upper = join_type.upper()
        super(Join, self).__init__(item, join_type_upper, join_item, on_using)
        if join_type.upper() not in ALLOWED_JOIN_TYPES:
            raise UnsupportedParameterError(join_type, 'join type')
        self.item = item
        self.join_type = join_type_upper
        self.join_item = join_item
        self.on_using = on_using

    def __sql__(self, engine):
        parts = [engine.as_value(self.item)]
        if self.join_type:
            parts.append(Sql(self.join_type))
        parts += [Sql(self.sql_name), engine.as_value(self.join_item)]
        if self.on_using is not None:
            parts.append(engine.as_value(self.on_using))
        return Sql(' ').join(parts)
