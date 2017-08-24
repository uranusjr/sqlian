from .base import Named, Sql


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

    def __init__(self, table_ref, column_ref=None):
        args = (table_ref,) if column_ref is None else (table_ref, column_ref,)
        super(InsertInto, self).__init__(*args)
        self.table_ref = table_ref
        self.column_ref = column_ref

    def __sql__(self):
        return Sql(' ').join([self.sql_name] + self.children)


class Values(Clause):
    pass


class Update(Clause):
    def __init__(self, table_ref):
        super(Update, self).__init__(table_ref)
        self.table_ref = table_ref


class Set(Clause):
    pass


class DeleteFrom(Clause):
    def __init__(self, table_ref):
        super(DeleteFrom, self).__init__(table_ref)
        self.table_ref = table_ref


class On(Clause):
    def __init__(self, condition):
        super(On, self).__init__(condition)


class Using(Clause):
    def __init__(self, using_list):
        super(Using, self).__init__(using_list)
