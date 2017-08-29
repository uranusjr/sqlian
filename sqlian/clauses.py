import collections

import six

from .base import Named, Parsable, Sql
from .compositions import Assign, List, Ordering
from .expressions import (
    And, Condition, Equal, In, Is, Ref, get_condition_classes,
)
from .utils import (
    is_flat_two_tuple, is_non_string_sequence, is_single_row,
    rstrip_composition_suffix,
)
from .values import Value, null


class Clause(Named, Parsable):

    def __init__(self, *children):
        super(Clause, self).__init__()
        self.children = list(children)

    def __repr__(self):
        return '{}({})'.format(
            self.type_name,
            ', '.join(repr(c) for c in self.children),
        )

    def __sql__(self):
        return Sql('{} {}').format(
            self.sql_name,
            Sql(', ').join(self.children),
        )

    @classmethod
    def parse(cls, value):
        # This is a rare case we extend parse(). Clauses contribute to the
        # output SQL, and therefore we need to make sure inner values are
        # wrapped in a Clause so the result SQL contains correct keywords.
        parsed = super(Clause, cls).parse(value)
        if isinstance(parsed, Clause):
            return parsed
        return cls(parsed)


class RefClause(Clause):

    def __init__(self, ref):
        super(RefClause, self).__init__(ref)

    @classmethod
    def parse_native(cls, value):
        return cls(Ref.parse(value))


class Select(Clause):
    @classmethod
    def parse_native(cls, value):
        # Special case: 2-string-tuple is AS instead of a list of columns.
        if is_flat_two_tuple(value):
            return cls(Ref.parse(value))
        if is_non_string_sequence(value):
            return cls(*(Ref.parse(v) for v in value))
        if not isinstance(value, six.string_types):
            return cls(Value.parse(value))
        return cls(Ref.parse(value))


class From(RefClause):
    pass


def parse_pair_as_condition(key, value):
    condition_classes = get_condition_classes()

    # Explicit tuple operator.
    if is_flat_two_tuple(key):
        key, klass = key
        if not isinstance(klass, Condition):
            try:
                klass = condition_classes[str(klass).upper()]
            except KeyError:
                raise ValueError('invalid operator {!r}'.format(klass))
        return klass(Ref.parse(key), Value.parse(value))

    # Parse in-key operator.
    for op, klass in condition_classes.items():
        if key.upper().endswith(' {}'.format(op)):
            return klass(
                Ref.parse(rstrip_composition_suffix(key, op)),
                Value.parse(value),
            )

    # Auto-detect operator based on right-hand value.
    parsed = Value.parse(value)
    if parsed is null:
        klass = Is
    elif isinstance(parsed, List):
        klass = In
    else:
        klass = Equal
    return klass(Ref.parse(key), parsed)


class Where(Clause):

    def __init__(self, condition):
        super(Where, self).__init__(condition)

    @classmethod
    def parse_native(cls, value):
        if isinstance(value, collections.Mapping):
            value = value.items()
        elif not isinstance(value, collections.Sequence):
            return cls(Value.parse(value))
        if is_single_row(value) and len(value) == 2:
            return cls(parse_pair_as_condition(*value))
        return cls(And(*(
            parse_pair_as_condition(key, value)
            for key, value in value
        )))


class GroupBy(RefClause):
    pass


class OrderBy(Clause):
    @classmethod
    def parse_native(cls, value):
        # Parse explicit operator tuple.
        if is_flat_two_tuple(value):
            return cls(Ordering(Ref.parse(value[0]), value[1]))

        # Parse in-key ordering.
        for ordering in Ordering.allowed_orderings:
            if value.upper().endswith(' {}'.format(ordering)):
                return cls(Ordering(
                    Ref.parse(rstrip_composition_suffix(value, ordering)),
                    ordering,
                ))

        # Treat this like a ref name.
        return cls(Ref.parse(value))


class Limit(Clause):
    def __init__(self, value):
        super(Limit, self).__init__(value)


class Offset(Clause):
    def __init__(self, value):
        super(Offset, self).__init__(value)


class InsertInto(RefClause):
    pass


class Columns(Clause):

    def __init__(self, ref_list):
        super(Columns, self).__init__(ref_list)
        self.ref_list = ref_list

    def __sql__(self):
        return self.ref_list.__sql__()

    @classmethod
    def parse_native(cls, value):
        return cls(List(*(Ref.parse(n) for n in value)))


class Values(Clause):

    def __init__(self, *children):
        super(Values, self).__init__(*children)

    @classmethod
    def parse_native(cls, value):
        if not value:
            return cls(List())
        if is_single_row(value):
            value = [value]
        return cls(*(
            List(*(Value.parse(v) for v in row))
            for row in value
        ))


class Update(RefClause):
    pass


class Set(Clause):
    @classmethod
    def parse_native(cls, value):
        if isinstance(value, collections.Mapping):
            value = value.items()
        elif not isinstance(value, collections.Sequence):
            return cls(Value.parse(value))
        if is_single_row(value) and len(value) == 2:
            k, v = value
            return cls(Assign(Ref.parse(k), Value.parse(v)))
        return cls(*(
            Assign(Ref.parse(k), Value.parse(v))
            for k, v in value
        ))


class DeleteFrom(RefClause):
    pass


class On(Clause):
    def __init__(self, condition):
        super(On, self).__init__(condition)


class Using(Clause):
    def __init__(self, using_list):
        super(Using, self).__init__(using_list)
