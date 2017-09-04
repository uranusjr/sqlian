import pytest

from sqlian import Sql, UnsupportedParameterError
from sqlian.standard import (
    compositions as m,
    constants as n,
    expressions as e,
    functions as f,
)


def test_as(engine):
    sql = m.As('Mosky', e.Identifier('name'))
    assert sql.__sql__(engine) == Sql('''
        'Mosky' AS "name"
    '''.strip())


def test_identifier_as(engine):
    sql = m.As(e.Identifier('person', 'name'), e.Identifier('name'))
    assert sql.__sql__(engine) == Sql('"person"."name" AS "name"')


def test_count_as(engine):
    sql = m.As(
        f.Count(e.Identifier('person', 'name')),
        e.Identifier('name_count'),
    )
    assert sql.__sql__(engine) == Sql('COUNT("person"."name") AS "name_count"')


def test_ordering(engine):
    sql = m.Ordering('Mosky', 'asc')
    assert sql.__sql__(engine) == Sql("'Mosky' ASC")


def test_ordering_identifier(engine):
    sql = m.Ordering(e.Identifier('name'), 'desc')
    assert sql.__sql__(engine) == Sql('"name" DESC')


def test_ordering_not_allowed(engine):
    with pytest.raises(UnsupportedParameterError) as ctx:
        m.Ordering(e.Identifier('name'), 'Bang!')
    assert str(ctx.value) == "unsupported ordering 'Bang!'"


def test_list(engine):
    sql = m.List('Mosky', 'TP')
    assert sql.__sql__(engine) == Sql("('Mosky', 'TP')")


def test_list_identifier(engine):
    sql = m.List(e.Identifier('name'), e.Identifier('age'))
    assert sql.__sql__(engine) == Sql('("name", "age")')


def test_list_mixed(engine):
    sql = m.List(e.Identifier('name'), n.star, 'Mosky')
    assert sql.__sql__(engine) == Sql('''
        ("name", *, 'Mosky')
    '''.strip())


def test_assign(engine):
    sql = m.Assign(e.Identifier('name'), 'Mosky')
    assert sql.__sql__(engine) == Sql('''
        "name" = 'Mosky'
    '''.strip())


def test_assign_identifier(engine):
    sql = m.Assign(e.Identifier('name'), e.Identifier('full_name'))
    assert sql.__sql__(engine) == Sql('"name" = "full_name"')


def test_join(engine):
    sql = m.Join(e.Identifier('person'), '', e.Identifier('detail'))
    assert sql.__sql__(engine) == Sql('"person" JOIN "detail"')


def test_join_typed(engine):
    sql = m.Join(
        e.Identifier('person'),
        'natural left', e.Identifier('detail'),
    )
    assert sql.__sql__(engine) == Sql('"person" NATURAL LEFT JOIN "detail"')


def test_join_not_allowed(engine):
    with pytest.raises(UnsupportedParameterError) as ctx:
        m.Join(
            e.Identifier('person'),
            '; DELETE FROM person --',
            e.Identifier('detail'),
        )
    assert str(ctx.value) == "unsupported join type '; DELETE FROM person --'"
