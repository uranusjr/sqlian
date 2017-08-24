from .base import Sql


class As(object):

    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias

    def __repr__(self):
        return '<Composition {!r} AS {}>'.format(self.expression, self.alias)

    def __sql__(self):
        return Sql('{} AS {}').format(self.expression, self.alias)


class Ordering(object):

    def __init__(self, expression, order):
        order = Sql(order.upper())
        if order not in ['ASC', 'DESC']:
            raise ValueError('unsupported ordering {!r}'.format(order))
        self.expression = expression
        self.order = order

    def __repr__(self):
        return '<Composition {!r} {}>'.format(self.expression, self.order)

    def __sql__(self):
        return Sql('{} {}').format(self.expression, self.order)


class List(object):

    def __init__(self, *children):
        self.children = list(children)

    def __repr__(self):
        return '<Composition {!r}>'.format(self.children)

    def __sql__(self):
        return Sql('({})').format(Sql(', ').join(self.children))
