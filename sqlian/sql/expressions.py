import collections
import inspect

from sqlian import compat, Sql


class Expression(object):
    pass


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
            Sql(engine.format_identifier(p))
            for p in self.qualified_parts
        )


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

    def __init__(self, lho, rho):
        super(Infix, self).__init__(lho, rho)

    def __sql__(self, engine):
        it = iter(self.operands)
        parts = [engine.as_sql(next(it))]
        for op in it:
            parts.append(Sql(
                self.alt_operators[op]
                if (isinstance(op, collections.Hashable) and
                    op in self.alt_operators)
                else self.operator
            ))
            parts.append(engine.as_sql(op))
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


@compat.lru_cache(maxsize=1)
def get_condition_classes():
    return {
        value.operator: value for value in globals().values()
        if inspect.isclass(value) and hasattr(value, 'operator')
    }
