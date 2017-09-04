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
        return Sql('{}({})').format(self.sql_name, Sql(', ').join(
            engine.format_value(v) for v in self.args
        ))


class Count(Function):
    sql_name = 'COUNT'
