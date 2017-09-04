from sqlian import Sql

from .expressions import Expression


class Function(Expression):

    def __init__(self, *args):
        super(Function, self).__init__()
        self.args = args

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__, ', '.join(repr(a) for a in self.args),
        )

    def __sql__(self, engine):
        return Sql('{}({})').format(Sql(self.sql_name), Sql(', ').join(
            engine.as_sql(v) for v in self.args
        ))


class Count(Function):

    sql_name = 'COUNT'

    def __init__(self, expression=None):
        args = [] if expression is None else [expression]
        super(Count, self).__init__(*args)
