from sqlian import Sql
from sqlian.sql import (
    compositions as m,
    expressions as e,
    functions as f,
)


def test_as(engine):
    sql = m.As('Mosky', 'name')
    assert sql.__sql__(engine) == Sql("""
        'Mosky' AS "name"
    """)


def test_identifier_as(engine):
    sql = m.As(e.Identifier('person', 'name'), 'name')
    assert sql.__sql__(engine) == Sql('"person"."name" AS "name"')


def test_count_as(engine):
    sql = m.As(f.Count(e.Identifier('person', 'name')), 'name_count')
    assert sql.__sql__(engine) == Sql('COUNT("person"."name") AS "name_count"')
