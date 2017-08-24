from .base import Named, Sql, ensure_sql
from .compositions import List
from .expressions import (
    Ref, parse_native_as_condition, parse_native_as_ref_list,
)
from .utils import is_non_string_sequence


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


class InsertInto(Clause):

    def __init__(self, table_ref):
        super(InsertInto, self).__init__(table_ref)

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, Ref))


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
        if any(not is_non_string_sequence(v) for v in values):
            values = [values]
        return cls(*(List(*v) for v in values))


class Update(Clause):

    def __init__(self, table_ref):
        super(Update, self).__init__(table_ref)

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, Ref))


class Set(Clause):
    pass


class DeleteFrom(Clause):

    def __init__(self, table_ref):
        super(DeleteFrom, self).__init__(table_ref)

    @classmethod
    def parse_native(cls, value):
        return cls(ensure_sql(value, Ref))


class On(Clause):
    def __init__(self, condition):
        super(On, self).__init__(condition)


class Using(Clause):
    def __init__(self, using_list):
        super(Using, self).__init__(using_list)
