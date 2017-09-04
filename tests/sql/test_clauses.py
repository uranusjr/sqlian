from sqlian import Sql
from sqlian.standard import (
    clauses as c,
    compositions as m,
    constants as n,
    expressions as e,
    functions as f,
)


def test_select(engine):
    sql = c.Select('Mosky')
    assert sql.__sql__(engine) == Sql("SELECT 'Mosky'")


def test_select_star(engine):
    sql = c.Select(n.star)
    assert sql.__sql__(engine) == Sql('SELECT *')


def test_select_identifier(engine):
    sql = c.Select(e.Identifier('name'))
    assert sql.__sql__(engine) == Sql('SELECT "name"')


def test_select_function(engine):
    sql = c.Select(f.Count())
    assert sql.__sql__(engine) == Sql('SELECT COUNT()')


def test_where(engine):
    sql = c.Where(True)
    assert sql.__sql__(engine) == Sql('WHERE TRUE')


def test_where_and(engine):
    sql = c.Where(e.And(
        e.Like(e.Identifier('name'), 'Mo%'),
        e.GreaterThan(e.Identifier('age'), 18),
    ))
    assert sql.__sql__(engine) == Sql('''
        WHERE "name" LIKE 'Mo%' AND "age" > 18
    '''.strip())


def test_order_by(engine):
    sql = c.OrderBy(e.Identifier('age'))
    assert sql.__sql__(engine) == Sql('ORDER BY "age"')


def test_order_by_ordering(engine):
    sql = c.OrderBy(m.Ordering(e.Identifier('age'), 'asc'))
    assert sql.__sql__(engine) == Sql('ORDER BY "age" ASC')


def test_order_by_multiple(engine):
    sql = c.OrderBy(
        m.Ordering(e.Identifier('age'), 'desc'),
        e.Identifier('name'),
    )
    assert sql.__sql__(engine) == Sql('ORDER BY "age" DESC, "name"')


def test_values_list(engine):
    sql = c.Values(m.List('Mosky', 42, e.Identifier('person', 'name')))
    assert sql.__sql__(engine) == Sql('''
        VALUES ('Mosky', 42, "person"."name")
    '''.strip())
