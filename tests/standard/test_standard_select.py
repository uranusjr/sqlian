import pytest

from sqlian import Sql
from sqlian.standard import Count, Value, star


def test_select_where_equal(engine):
    sql = engine.select(
        'person_id', from_='person', where={'person_id': 'mosky'},
    )
    assert sql == Sql('''
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())


def test_select_where_like(engine):
    sql = engine.select(
        from_='person',
        where={'name like': 'Mosky%'},
        offset=1, limit=3,
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1
    '''.strip())


def test_select_where_in(engine):
    sql = engine.select(
        from_='person',
        where=[(('person_id', 'in'), ['andy', 'bob'])],
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')
    '''.strip())


def test_select_where_is_null(engine):
    sql = engine.select(
        from_='person',
        where={'name': None},
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "name" IS NULL
    '''.strip())


def test_select_where_greater_than_like(engine):
    sql = engine.select(
        from_='person', where={'age >': 20, 'name LIKE': 'Mosky%'},
    )
    assert sql in (   # Either one works.
        Sql("""
            SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'
        """.strip()),
        Sql("""
            SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' AND "age" > 20
        """.strip()),
    )


def test_select_where_false(engine):
    sql = engine.select(from_='person', where=False)
    assert sql == Sql('SELECT * FROM "person" WHERE FALSE')


def test_select_from(engine):
    sql = engine.select(from_='person')
    assert sql == Sql('SELECT * FROM "person"')


def test_select_from_multiple(engine):
    sql = engine.select(from_=('person', 'detail'))
    assert sql == Sql('SELECT * FROM "person", "detail"')


def test_select_from_one(engine):
    sql = engine.select(from_=['person'])
    assert sql == Sql('SELECT * FROM "person"')


def test_select_constant(engine):
    sql = engine.select(1)
    assert sql == Sql('SELECT 1')


def test_select_string_constant(engine):
    sql = engine.select(Value('foo'))
    assert sql == Sql("SELECT 'foo'")


def test_select_qualified(engine):
    sql = engine.select('person.person_id', 'person.name', from_='person')
    assert sql == Sql(
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_list(engine):
    sql = engine.select(['person.person_id', 'person.name'], from_='person')
    assert sql == Sql(
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_as(engine):
    sql = engine.select(
        ('person.person_id', 'id'), 'person.name', from_='person',
    )
    assert sql == Sql(
        'SELECT "person"."person_id" AS "id", "person"."name" FROM "person"'
    )


def test_select_qualified_as_single(engine):
    sql = engine.select(('person.person_id', 'id'), from_='person')
    assert sql == Sql('SELECT "person"."person_id" AS "id" FROM "person"')


def test_select_qualified_as_single_in_list(engine):
    sql = engine.select([('person.person_id', 'id')], from_='person')
    assert sql == Sql('SELECT "person"."person_id" AS "id" FROM "person"')


def test_select_order_by(engine):
    sql = engine.select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        orderby='age',
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"
    '''.strip())


def test_select_order_by_desc(engine):
    sql = engine.select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        orderby=('age', 'desc'),
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    '''.strip())


def test_select_order_by_desc_parse(engine):
    sql = engine.select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        order='age desc',
    )
    assert sql == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    '''.strip())


@pytest.mark.xfail(reason='Need more thought how to do native param well.')
def test_select_param(engine):
    sql = engine.select(from_='table', where={})
    assert sql == Sql(
        'SELECT * FROM "table" '
        'WHERE "auto_param" = %(auto_param)s '
        'AND "using_alias" = %(using_alias)s '
        'AND "custom_param" = %(my_param)s'
    )


def test_select_count(engine):
    sql = engine.select(Count(star), from_='person', group_by='age')
    assert sql == Sql('SELECT COUNT(*) FROM "person" GROUP BY "age"')


def test_select_join_natural(engine):
    sql = engine.select(from_=('person', engine.join.natural('detail')))
    assert sql == Sql('SELECT * FROM "person" NATURAL JOIN "detail"')


def test_select_join_inner_on(engine):
    sql = engine.select(from_=('person', engine.join.inner('detail', on={
        'person.person_id': 'detail.person_id',
    })))
    assert sql == Sql(
        'SELECT * FROM "person" '
        'INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"'
    )


def test_select_join_left_using(engine):
    sql = engine.select(from_=(
        'person', engine.join.left('detail', using='person_id'),
    ))
    assert sql == Sql('''
        SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")
    '''.strip())


def test_select_join_cross(engine):
    sql = engine.select(from_=('person', engine.join.cross('detail')))
    assert sql == Sql('SELECT * FROM "person" CROSS JOIN "detail"')


def test_select_join_right_using(engine):
    sql = engine.select(from_=(
        'person', engine.join.right('detail', using=['person_id']),
    ))
    assert sql == Sql('''
        SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")
    '''.strip())
