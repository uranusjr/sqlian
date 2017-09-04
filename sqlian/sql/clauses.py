from sqlian import Sql


class Clause(object):

    def __init__(self, *children):
        super(Clause, self).__init__()
        self.children = list(children)

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join(repr(c) for c in self.children),
        )

    def __sql__(self, engine):
        return Sql('{} {}').format(
            Sql(self.sql_name),
            Sql(', ').join(engine.as_value(c) for c in self.children),
        )


class Select(Clause):
    sql_name = 'SELECT'


class From(Clause):
    sql_name = 'FROM'


class Where(Clause):
    sql_name = 'WHERE'


class GroupBy(Clause):
    sql_name = 'GROUP BY'


class OrderBy(Clause):
    sql_name = 'ORDER BY'


class Limit(Clause):
    sql_name = 'LIMIT'


class Offset(Clause):
    sql_name = 'OFFSET'


class InsertInto(Clause):
    sql_name = 'INSERT INTO'


class Columns(Clause):
    sql_name = 'COLUMNS'


class Values(Clause):
    sql_name = 'VALUES'


class Update(Clause):
    sql_name = 'UPDATE'


class Set(Clause):
    sql_name = 'SET'


class DeleteFrom(Clause):
    sql_name = 'DELETE FROM'


class On(Clause):
    sql_name = 'ON'


class Using(Clause):
    sql_name = 'USING'
