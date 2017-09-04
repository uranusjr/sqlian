import collections

from sqlian import Parsable, Sql, is_single_row
from sqlian.utils import is_flat_two_tuple

from .compositions import List
from .expressions import (
    Condition, Identifier, Value,
    get_condition_classes,
    And, Equal, In,
)


class Clause(Parsable):

    def __init__(self, *children):
        super(Clause, self).__init__()
        self.children = list(children)

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join(repr(c) for c in self.children),
        )

    def __sql__(self, engine):
        arg_sql = Sql(', ').join(engine.as_value(c) for c in self.children)
        if not self.sql_name:
            return arg_sql
        return Sql('{} {}').format(Sql(self.sql_name), arg_sql)

    @classmethod
    def parse(cls, value, engine):
        # This is a rare case we extend parse(). Clauses contribute to the
        # output SQL, and therefore we need to make sure inner values are
        # wrapped in a Clause so the result SQL contains correct keywords.
        parsed = super(Clause, cls).parse(value, engine)
        if isinstance(parsed, Clause):
            return parsed
        return cls(parsed)


class IdentifierClause(Clause):
    @classmethod
    def parse_native(cls, value, engine):
        return cls(Identifier.parse(value, engine))


class Select(Clause):
    sql_name = 'SELECT'


class From(Clause):
    sql_name = 'FROM'


def parse_pair_as_condition(pair, engine, rho_klass):
    key, value = pair
    condition_classes = get_condition_classes()

    # Explicit tuple operator.
    if is_flat_two_tuple(key):
        key, klass = key
        if not isinstance(klass, Condition):
            try:
                klass = condition_classes[str(klass).upper()]
            except KeyError:
                raise ValueError('invalid operator {!r}'.format(klass))
        return klass(
            Identifier.parse(key, engine),
            rho_klass.parse(value, engine),
        )

    # Parse in-key operator.
    for op, klass in condition_classes.items():
        if key.upper().endswith(' {}'.format(op)):
            return klass(
                Identifier.parse(key[:-(len(op) + 1)], engine),
                rho_klass.parse(value, engine),
            )

    # Auto-detect operator based on right-hand value.
    parsed = rho_klass.parse(value, engine)
    if isinstance(parsed, List):
        klass = In
    else:
        klass = Equal
    return klass(Identifier.parse(key, engine), parsed)


def parse_as_condition(value, engine, rho_klass=Value):
    if isinstance(value, collections.Mapping):
        value = value.items()
    elif not isinstance(value, collections.Sequence):
        return value
    if is_single_row(value) and len(value) == 2:
        return parse_pair_as_condition(value, engine, rho_klass=rho_klass)
    return And(*(
        parse_pair_as_condition((key, value), engine, rho_klass=rho_klass)
        for key, value in value
    ))


class Where(Clause):

    sql_name = 'WHERE'

    @classmethod
    def parse_native(cls, value, engine):
        return cls(parse_as_condition(value, engine))


class GroupBy(IdentifierClause):
    sql_name = 'GROUP BY'


class OrderBy(Clause):
    sql_name = 'ORDER BY'


class Limit(Clause):
    sql_name = 'LIMIT'


class Offset(Clause):
    sql_name = 'OFFSET'


class InsertInto(IdentifierClause):
    sql_name = 'INSERT INTO'


class Columns(Clause):
    sql_name = ''


class Values(Clause):
    sql_name = 'VALUES'


class Update(IdentifierClause):
    sql_name = 'UPDATE'


class Set(Clause):
    sql_name = 'SET'


class DeleteFrom(IdentifierClause):
    sql_name = 'DELETE FROM'


class On(Clause):
    sql_name = 'ON'


class Using(Clause):
    sql_name = 'USING'
