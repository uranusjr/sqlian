import collections

import six

from sqlian import Parsable, Sql, is_single_row
from sqlian.utils import (
    is_flat_tuple, is_flat_two_tuple,
    is_non_string_sequence, is_partial_of,
)

from .compositions import Assign, Join, List, Ordering
from .expressions import (
    Condition, Identifier, Value,
    get_condition_classes,
    And, Equal, In,
)


__all__ = [
    'Clause', 'IdentifierClause',
    'Select', 'From', 'Where', 'On', 'Using',
    'GroupBy', 'OrderBy', 'Limit', 'Offset',
    'InsertInto', 'Columns', 'Values',
    'Update', 'Set',
    'DeleteFrom',
]


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
        if not self.children:
            return self.sql_name
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

    @classmethod
    def parse_native(cls, value, engine):
        # Special case: 2-string-tuple is AS instead of a sequence of columns.
        if is_flat_two_tuple(value):
            return cls(Identifier.parse(value, engine))
        if is_non_string_sequence(value):
            return cls(*(Identifier.parse(v, engine) for v in value))
        if not isinstance(value, six.string_types):
            return cls(value)
        return cls(Identifier.parse(value, engine))


def parse_from_argument(value, engine):
    if is_flat_tuple(value) and all(callable(v) for v in value[1:]):
        item = Identifier.parse(value[0], engine)
        for v in value[1:]:
            item = v(item)
        return item
    return Identifier.parse(value, engine)


class From(Clause):

    sql_name = 'FROM'

    @classmethod
    def parse_native(cls, value, engine):
        # Special case: (Any, Join, ...) tuple is JOIN, not from-item sequence.
        if (is_flat_tuple(value) and
                all(is_partial_of(v, Join) for v in value[1:])):
            return cls(parse_from_argument(value, engine))
        if is_non_string_sequence(value):
            return cls(*(parse_from_argument(v, engine) for v in value))
        return cls(parse_from_argument(value, engine))


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

    @classmethod
    def parse_native(cls, value, engine):
        # Parse explicit operator tuple.
        if is_flat_two_tuple(value):
            return cls(Ordering(Identifier.parse(value[0], engine), value[1]))

        # Parse in-key ordering.
        for ordering in Ordering.allowed_orderings:
            if value.upper().endswith(' {}'.format(ordering)):
                return cls(Ordering(
                    Identifier.parse(value[:-(len(ordering) + 1)], engine),
                    ordering,
                ))

        # Treat this like a ref name.
        return cls(Identifier.parse(value, engine))


class Limit(Clause):
    sql_name = 'LIMIT'


class Offset(Clause):
    sql_name = 'OFFSET'


class InsertInto(IdentifierClause):
    sql_name = 'INSERT INTO'


class Columns(Clause):

    sql_name = ''

    @classmethod
    def parse_native(cls, value, engine):
        return cls(List(*(Identifier.parse(n, engine) for n in value)))


class Values(Clause):

    sql_name = 'VALUES'

    @classmethod
    def parse_native(cls, value, engine):
        if not value:
            return cls(List())
        if is_single_row(value):
            value = [value]
        return cls(*(List(*row) for row in value))


class Update(IdentifierClause):
    sql_name = 'UPDATE'


class Set(Clause):

    sql_name = 'SET'

    @classmethod
    def parse_native(cls, value, engine):
        if isinstance(value, collections.Mapping):
            value = value.items()
        elif not isinstance(value, collections.Sequence):
            return cls(value)
        if is_single_row(value) and len(value) == 2:
            k, v = value
            return cls(Assign(Identifier.parse(k, engine), v))
        return cls(*(
            Assign(Identifier.parse(k, engine), v)
            for k, v in value
        ))


class DeleteFrom(IdentifierClause):
    sql_name = 'DELETE FROM'


class On(Clause):

    sql_name = 'ON'

    @classmethod
    def parse_native(cls, value, engine):
        return cls(parse_as_condition(value, engine, rho_klass=Identifier))


class Using(Clause):

    sql_name = 'USING'

    @classmethod
    def parse_native(cls, value, engine):
        if not is_non_string_sequence(value):
            value = [value]
        return cls(List(*(Identifier.parse(v, engine) for v in value)))
