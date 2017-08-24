from .base import Named, Sql
from .expressions import Expression


class Function(Named, Expression):

    def __init__(self, *args):
        super(Function, self).__init__()
        self.args = args

    def __repr__(self):
        return '{}({})'.format(
            self.type_name, ', '.join(repr(a) for a in self.args),
        )

    def __sql__(self):
        return Sql('{}({})').format(self.sql_name, Sql(', ').join(self.args))


class Count(Function):
    pass
