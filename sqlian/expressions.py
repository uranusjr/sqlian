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


class Condition(Expression):
    """Condition is a specialized expression that evaluates to a boolean.
    """


class UnarySuffix(Condition):

    def __init__(self, p):
        self.operand = p

    def __repr__(self):
        return '<Condition {!r}>'.format(str(sql(self)))

    def __sql__(self):
        return Sql('{0} {op}').format(self.operand, op=Sql(self.operator))


class BinaryInfix(Condition):

    def __init__(self, p1, p2):
        self.operands = (p1, p2)

    def __repr__(self):
        return '<Condition {!r}>'.format(str(sql(self)))

    def __sql__(self):
        kwargs = {'op': Sql(self.operator)}     # Python 2 & 3.4 compatibility.
        return Sql('{0} {op} {1}').format(*self.operands, **kwargs)


class IsNull(UnarySuffix):
    operator = 'IS NULL'


class IsNotNull(UnarySuffix):
    operator = 'IS NOT NULL'


class Equal(BinaryInfix):
    operator = '='


class NotEqual(BinaryInfix):
    operator = '!='


class GreaterThan(BinaryInfix):
    operator = '>'


class LessThan(BinaryInfix):
    operator = '<'


class GreaterThanOrEqual(BinaryInfix):
    operator = '>='


class LessThanOrEqual(BinaryInfix):
    operator = '<='


class Like(BinaryInfix):
    operator = 'LIKE'


class In(BinaryInfix):

    operator = 'IN'

    def __sql__(self):
        return Sql('{0} {op} ({1})').format(
            self.operands[0], Sql(', ').join(self.operands[1]),
            op=Sql(self.operator),
        )


class And(BinaryInfix):

    operator = 'AND'

    def __sql__(self):
        return Sql('({0}) {op} ({1})').format(
            self.operands[0], self.operands[1],
            op=Sql(self.operator),
        )
