import collections
import inspect

from sqlian import compat, Parsable, Sql
from sqlian.utils import is_flat_two_tuple, is_non_string_sequence

from .compositions import As, List


__all__ = [
    'Expression',
    'Identifier', 'Parameter', 'Value',

    'Condition', 'Infix',
    'Equal', 'NotEqual', 'GreaterThan', 'LessThan', 'GreaterThanOrEqual',
    'LessThanOrEqual', 'Like', 'In', 'And', 'Or', 'Add', 'Substract',
    'Multiply', 'Divide',

    'get_condition_classes',
]


class Expression(Parsable):
    pass


class Value(Expression):
    """Wrapper for a plain value.

    This is useful when a native value is parsed as an identifier by default.
    Wrap your variable inside this class to declare it as a value explicitly.
    """
    def __init__(self, wrapped):
        super(Value, self).__init__()
        self.wrapped = wrapped

    def __repr__(self):
        return 'Value({!r})'.format(self.wrapped)

    def __sql__(self, engine):
        return engine.as_value(self.wrapped)

    def __hash__(self):
        return hash(self.wrapped)

    def __eq__(self, other):
        return self.wrapped == other

    @classmethod
    def parse_native(cls, value, engine):
        if is_non_string_sequence(value):
            return List(*(cls.parse(v, engine) for v in value))
        return super(Value, cls).parse_native(value, engine)


class Identifier(Expression):

    def __init__(self, *qualified_parts):
        super(Identifier, self).__init__()
        self.qualified_parts = list(qualified_parts)

    def __repr__(self):
        return 'Id({})'.format(
            '.'.join(repr(p) for p in self.qualified_parts),
        )

    def __sql__(self, engine):
        return Sql('.').join(
            Sql(engine.as_identifier(p))
            for p in self.qualified_parts
        )

    @classmethod
    def parse_native(cls, value, engine):
        if is_flat_two_tuple(value):
            exp, alias = value
            return As(cls.parse(exp, engine), Identifier.parse(alias, engine))
        return cls(*(
            part[1:-1] if (
                part.startswith(engine.identifier_quote) and
                part.endswith(engine.identifier_quote)
            ) else part
            for part in value.split('.')
        ))


class Parameter(Expression):

    def __init__(self, name):
        super(Parameter, self).__init__()
        self.name = name

    def __repr__(self):
        return 'Param({})'.format(self.name)

    def __sql__(self, engine):
        return Sql('%({})s'.format(self.name))


class Condition(Expression):
    """Condition is a specialized expression that evaluates to a boolean.
    """
    alt_operators = {}

    def __init__(self, *ps):
        self.operands = ps

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join(repr(o) for o in self.operands),
        )


class Infix(Condition):
    def __sql__(self, engine):
        it = iter(self.operands)
        parts = [engine.as_value(next(it))]
        for op in it:
            parts.append(Sql(
                self.alt_operators[op]
                if (isinstance(op, collections.Hashable) and
                    op in self.alt_operators)
                else self.operator
            ))
            parts.append(engine.as_value(op))
        return Sql(' '.join(parts))


class Equal(Infix):
    operator = '='
    alt_operators = {None: 'IS'}


class NotEqual(Infix):
    operator = '!='
    alt_operators = {None: 'IS NOT'}


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


class Or(Infix):
    operator = 'OR'


class Add(Infix):
    operator = '+'


class Substract(Infix):
    operator = '-'


class Multiply(Infix):
    operator = '*'


class Divide(Infix):
    operator = '/'


@compat.lru_cache(maxsize=1)
def get_condition_classes():
    return {
        value.operator: value for value in globals().values()
        if inspect.isclass(value) and hasattr(value, 'operator')
    }
