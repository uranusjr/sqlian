import collections
import functools
import inspect

from .base import UnescapedError, Sql, sql
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

    def __eq__(self, operand):
        return Equal(self, operand)


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


@functools.lru_cache(maxsize=1)
def get_condition_classes():
    return {
        value.operator: value for value in globals().values()
        if inspect.isclass(value) and hasattr(value, 'operator')
    }


def parse_pair_as_condition(key, value):
    condition_classes = get_condition_classes()
    if isinstance(key, tuple):
        key, op = key
        return condition_classes[op](Ref(key), value)
    for op, klass in condition_classes.items():
        if key.endswith(' {}'.format(op)):
            return klass(Ref(key[:-(len(op) + 1)]), value)
    return Equal(Ref(key), value)


def parse_native_as_condition(data):
    if isinstance(data, collections.Mapping):
        data = data.items()
    elif not isinstance(data, collections.Sequence):
        return sql(data)
    return And(*(parse_pair_as_condition(key, value) for key, value in data))
