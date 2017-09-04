from sqlian import Sql
from sqlian.sql import expressions as e


def test_identifier(engine):
    sql = e.Identifier('foo')
    assert sql.__sql__(engine) == Sql('"foo"'), sql


def test_identifier_qualified(engine):
    sql = e.Identifier('foo', 'bar')
    assert sql.__sql__(engine) == Sql('"foo"."bar"'), sql


def test_is_null(engine):
    sql = e.Equal(e.Identifier('foo'), None)
    assert sql.__sql__(engine) == Sql('"foo" IS NULL'), sql


def test_is_not_null(engine):
    sql = e.NotEqual(e.Identifier('foo'), None)
    assert sql.__sql__(engine) == Sql('"foo" IS NOT NULL'), sql


def test_equal(engine):
    sql = e.Equal(e.Identifier('foo', 'bar'), 42)
    assert sql.__sql__(engine) == Sql('"foo"."bar" = 42'), sql


def test_not_equal(engine):
    sql = e.NotEqual(e.Identifier('person', 'name'), 'Mosky')
    assert sql.__sql__(engine) == Sql('"person"."name" != ' + "'Mosky'"), sql
