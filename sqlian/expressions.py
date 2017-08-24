from .base import Sql, sql
from .utils import sql_format_identifier


class Expression(object):
    pass


class Star(Expression):

    def __repr__(self):
        return '<Star>'

    def __sql__(self):
        return Sql('*')


star = Star()


class Ref(Expression):

    def __init__(self, *qualified_parts):
        super(Ref, self).__init__()
        self.qualified_parts = list(qualified_parts)

    def __repr__(self):
        return '<Ref {}>'.format(
            '.'.join(repr(p) for p in self.qualified_parts),
        )

    def __sql__(self):
        return Sql('.').join(
            Sql(sql_format_identifier(p)) for p in self.qualified_parts
        )


class Param(Expression):

    def __init__(self, name):
        super(Param, self).__init__()
        self.name = name

    def __repr__(self):
        return '<Param %({})s>'.format(self.name)

    def __sql__(self):
        return Sql('%({})s'.format(self.name))


class Condition(Expression):
    """Condition is a specialized expression that evaluates to a boolean.
    """
    def __init__(self, *ps):
        self.operands = ps

    def __repr__(self):
        return 'Condition({!r})'.format(str(sql(self)))


class Suffix(Condition):
    def __sql__(self):
        return Sql('{} {}').format(
            Sql(' ').join(self.operands), Sql(self.operator),
        )


class Infix(Condition):
    def __sql__(self):
        return Sql(' {} '.format(self.operator)).join(self.operands)


class IsNull(Suffix):
    operator = 'IS NULL'


class IsNotNull(Suffix):
    operator = 'IS NOT NULL'


class Equal(Infix):
    operator = '='


class NotEqual(Infix):
    operator = '!='


class GreaterThan(Infix):
    operator = '>'


class LessThan(Infix):
    operator = '<'


class GreaterThanOrEqual(Infix):
    operator = '>='


class LessThanOrEqual(Infix):
    operator = '<='


class Like(Infix):
    operator = 'LIKE'


class In(Infix):
    operator = 'IN'


class And(Infix):
    operator = 'AND'
