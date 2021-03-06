from sqlian import Sql
from sqlian.standard import (
    clauses as c,
    compositions as m,
    constants as n,
    expressions as e,
    functions as f,
    statements as s,
)


def test_select(engine):
    sql = s.Select(
        c.Select(e.Identifier('name')),
        c.From(e.Identifier('person')),
    )
    assert sql.__sql__(engine) == Sql('SELECT "name" FROM "person"')


def test_select_where(engine):
    sql = s.Select(
        c.Select(e.Identifier('name')),
        c.From(e.Identifier('person')),
        c.Where(False)
    )
    assert sql.__sql__(engine) == Sql('''
        SELECT "name" FROM "person" WHERE FALSE
    '''.strip())


def test_select_where_condition(engine):
    sql = s.Select(
        c.Select(e.Identifier('name')),
        c.From(e.Identifier('person')),
        c.Where(e.Or(
            e.Like(e.Identifier('name'), 'Mo%'),
            e.GreaterThanOrEqual(e.Identifier('age'), 18),
        )),
    )
    assert sql.__sql__(engine) == Sql('''
        SELECT "name" FROM "person" WHERE "name" LIKE 'Mo%' OR "age" >= 18
    '''.strip())


def test_select_where_subquery_as(engine):
    sql = s.Select(
        c.Select(
            e.Identifier('t', n.star),
            m.As(e.Add(e.Identifier('a'), e.Identifier('b')),
                 e.Identifier('total')),
        ),
        c.From(m.As(m.List(
            s.Select(
                c.Select(
                    m.As(f.Sum(e.Identifier('c1')), e.Identifier('a')),
                    m.As(f.Sum(e.Identifier('c2')), e.Identifier('b')),
                ),
                c.From(e.Identifier('table')),
            ),
        ), e.Identifier('t'))),
    )
    assert sql.__sql__(engine) == Sql(
        'SELECT "t".*, "a" + "b" AS "total" FROM ('
        'SELECT SUM("c1") AS "a", SUM("c2") AS "b" FROM "table"'
        ') AS "t"'
    )
