from .base import Named, Sql


class Clause(Named):

    def __init__(self, *children):
        super(Clause, self).__init__()
        self.children = list(children)

    def __repr__(self):
        return '<{} {!r}>'.format(self.type_name, self.children)

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
        super(InsertInto, self).__init__(table_ref, column_ref)
        self.table_ref = table_ref
        self.column_ref = column_ref

    def __repr__(self):
        return '<{} {!r} {!r}>'.format(
            self.type_name, self.table_ref, self.column_ref,
        )

    def __sql__(self):
        if self.column_ref is None:
            template = Sql('{sql_name} {table_ref}')
        else:
            template = Sql('{sql_name} {table_ref} {column_ref}')
        return template.format(
            sql_name=self.sql_name, table_ref=self.table_ref,
            column_ref=self.column_ref,
        )


class Values(Clause):
    pass
