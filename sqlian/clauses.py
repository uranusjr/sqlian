import collections

from .base import Named, Sql, ensure_sql, sql
from .compositions import Assign, List
from .expressions import And, Equal, Ref, get_condition_classes
from .utils import is_single_row


class Clause(Named):

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


class TableClause(Clause):

    def __init__(self, ref):
        super(TableClause, self).__init__(ref)

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, Ref))


class Select(Clause):
    pass


class From(Clause):
    pass


class Where(Clause):

    def __init__(self, condition):
        super(Where, self).__init__(condition)

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, parse_native_as_condition))


class GroupBy(Clause):
    pass


class OrderBy(Clause):
    pass


class Limit(Clause):
    def __init__(self, value):
        super(Limit, self).__init__(value)


class Offset(Clause):
    def __init__(self, value):
        super(Offset, self).__init__(value)


class InsertInto(TableClause):
    pass


class Columns(Clause):

    def __init__(self, ref_list):
        super(Columns, self).__init__(ref_list)
        self.ref_list = ref_list

    def __sql__(self):
        return self.ref_list.__sql__()

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, parse_native_as_ref_list))


class Values(Clause):

    def __init__(self, *children):
        super(Values, self).__init__(*children)

    @classmethod
    def parse_native(cls, values):
        if not values:
            return cls(List())
        if is_single_row(values):
            values = [values]
        return cls(*(List(*v) for v in values))


class Update(TableClause):
    pass


class Set(Clause):
    @classmethod
    def parse_native(cls, values):
        if isinstance(values, collections.Mapping):
            values = values.items()
        elif not isinstance(values, collections.Sequence):
            return cls(values)
        return cls(*(
            Assign(ensure_sql(key, Ref), value)
            for key, value in values
        ))


class DeleteFrom(TableClause):
    pass


class On(Clause):
    def __init__(self, condition):
        super(On, self).__init__(condition)


class Using(Clause):
    def __init__(self, using_list):
        super(Using, self).__init__(using_list)


# Native construct parsers.

def parse_pair_as_condition(key, value):
    condition_classes = get_condition_classes()
    if isinstance(key, tuple):
        key, op = key
        return condition_classes[op](Ref(key), value)
    for op, klass in condition_classes.items():
        if key.endswith(' {}'.format(op)):
            return klass(Ref(key[:-(len(op) + 1)]), value)
    return Equal(ensure_sql(key, Ref), value)


def parse_native_as_condition(data):
    if isinstance(data, collections.Mapping):
        data = data.items()
    elif not isinstance(data, collections.Sequence):
        return sql(data)
    return And(*(parse_pair_as_condition(key, value) for key, value in data))


def parse_native_as_ref_list(names):
    return List(*(Ref(n) for n in names))
