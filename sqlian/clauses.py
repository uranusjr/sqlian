from .base import Named, Sql, ensure_sql, ensure_sql_args
from .compositions import parse_native_as_value_list
from .expressions import (
    Ref, parse_native_as_condition, parse_native_as_ref_list,
)


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
    @ensure_sql(parse_native_as_condition)
    def __init__(self, condition):
        super(Where, self).__init__(condition)


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
    @ensure_sql(Ref)
    def __init__(self, table_ref):
        super(InsertInto, self).__init__(table_ref)


class Columns(Clause):

    @ensure_sql(parse_native_as_ref_list)
    def __init__(self, ref_list):
        super(Columns, self).__init__(ref_list)
        self.ref_list = ref_list

    def __sql__(self):
        return self.ref_list.__sql__()


class Values(Clause):
    @ensure_sql_args(parse_native_as_value_list, skip_first=True)
    def __init__(self, *children):
        super(Values, self).__init__(*children)


class Update(Clause):
    @ensure_sql(Ref)
    def __init__(self, table_ref):
        super(Update, self).__init__(table_ref)


class Set(Clause):
    pass


class DeleteFrom(Clause):
    @ensure_sql(Ref)
    def __init__(self, table_ref):
        super(DeleteFrom, self).__init__(table_ref)


class On(Clause):
    def __init__(self, condition):
        super(On, self).__init__(condition)


class Using(Clause):
    def __init__(self, using_list):
        super(Using, self).__init__(using_list)
