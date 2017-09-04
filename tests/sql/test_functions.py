from sqlian import Sql
from sqlian.standard import (
    constants as n,
    expressions as e,
    functions as f,
)


def test_count(engine):
    sql = f.Count()
    assert sql.__sql__(engine) == Sql('COUNT()'), sql


def test_count_star(engine):
    sql = f.Count(n.star)
    assert sql.__sql__(engine) == Sql('COUNT(*)'), sql


def test_count_value(engine):
    sql = f.Count('Mosky')
    assert sql.__sql__(engine) == Sql("COUNT('Mosky')"), sql


def test_count_identifier(engine):
    sql = f.Count(e.Identifier('name'))
    assert sql.__sql__(engine) == Sql('COUNT("name")'), sql


def test_count_expression(engine):
    sql = f.Count(e.Equal(e.Identifier('name'), 'Mosky'))
    assert sql.__sql__(engine) == Sql('''COUNT("name" = 'Mosky')'''), sql
