import inspect

from . import compat
from .base import Parsable, Sql
from .compositions import As
from .utils import is_flat_two_tuple, sql_format_identifier
from .values import Value, null


class Expression(Parsable):
    pass


class Ref(Expression):

    def __init__(self, *qualified_parts):
        super(Ref, self).__init__()
        self.qualified_parts = list(qualified_parts)

    def __repr__(self):
        return 'Ref({})'.format(
            '.'.join(repr(p) for p in self.qualified_parts),
        )

    def __sql__(self):
        return Sql('.').join(
            Sql(sql_format_identifier(p)) for p in self.qualified_parts
        )

    def __eq__(self, operand):
        if operand is null:
            return Is(self, null)
        return Equal(self, Value.parse(operand))

    @classmethod
    def parse_native(cls, value):
        if is_flat_two_tuple(value):
            exp, alias = value
            return As(cls.parse(exp), Ref.parse(alias))
        return cls(*value.split('.'))


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
        return '{}({})'.format(
            type(self),
            ', '.join(repr(o) for o in self.operands),
        )


class Infix(Condition):
    def __sql__(self):
        return Sql(' {} '.format(self.operator)).join(self.operands)


class Is(Infix):
    operator = 'IS'


class IsNot(Infix):
    operator = 'IS NOT'


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


@compat.lru_cache(maxsize=1)
def get_condition_classes():
    return {
        value.operator: value for value in globals().values()
        if inspect.isclass(value) and hasattr(value, 'operator')
    }
