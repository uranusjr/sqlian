from sqlian import Sql


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
            engine.as_sql(self.expression),
            engine.format_identifier(self.alias),
        )
