import pytest

from sqlian import Count, Value, join, select, star


def test_select_where_equal():
    query = select('person_id', from_='person', where={'person_id': 'mosky'})
    assert query == """
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_select_where_like():
    query = select(
        from_='person',
        where={'name like': 'Mosky%'},
        offset=1, limit=3,
    )
    assert query == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1
    """.strip()


def test_select_where_in():
    query = select(
        from_='person',
        where=[
            (('person_id', 'in'), ['andy', 'bob']),
        ],
    )
    assert query == """
        SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')
    """.strip()


def test_select_where_is_null():
    query = select(
        from_='person',
        where={'name': None},
    )
    assert query == """
        SELECT * FROM "person" WHERE "name" IS NULL
    """.strip()


def test_select_where_greater_than_like():
    query = select(from_='person', where={'age >': 20, 'name LIKE': 'Mosky%'})
    assert query in (   # Either one works.
        """SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'""",
        """SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' AND "age" > 20""",
    )


def test_select_where_false():
    query = select(from_='person', where=False)
    assert query == 'SELECT * FROM "person" WHERE FALSE'


def test_select_from():
    query = select(from_='person')
    assert query == 'SELECT * FROM "person"'


def test_select_from_multiple():
    query = select(from_=('person', 'detail'))
    assert query == 'SELECT * FROM "person", "detail"'


def test_select_from_one():
    query = select(from_=['person'])
    assert query == 'SELECT * FROM "person"'


def test_select_constant():
    query = select(1)
    assert query == 'SELECT 1'


def test_select_string_constant():
    query = select(Value('foo'))
    assert query == "SELECT 'foo'"


def test_select_qualified():
    query = select('person.person_id', 'person.name', from_='person')
    assert query == (
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_list():
    query = select(['person.person_id', 'person.name'], from_='person')
    assert query == (
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_as():
    query = select(('person.person_id', 'id'), 'person.name', from_='person')
    assert query == (
        'SELECT "person"."person_id" AS "id", "person"."name" FROM "person"'
    )


def test_select_qualified_as_single():
    query = select(('person.person_id', 'id'), from_='person')
    assert query == 'SELECT "person"."person_id" AS "id" FROM "person"'


def test_select_qualified_as_single_in_list():
    query = select([('person.person_id', 'id')], from_='person')
    assert query == 'SELECT "person"."person_id" AS "id" FROM "person"'


def test_select_order_by():
    query = select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        orderby='age',
    )
    assert query == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"
    """.strip()


def test_select_order_by_desc():
    query = select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        orderby=('age', 'desc'),
    )
    assert query == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    """.strip()


def test_select_order_by_desc_parse():
    query = select(
        from_='person',
        where={('name', 'like'): 'Mosky%'},
        order='age desc',
    )
    assert query == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    """.strip()


@pytest.mark.skip(reason='Need more thought how to do native param well.')
def test_select_param():
    query = select()
    assert query == (
        'SELECT * FROM "table" '
        'WHERE "auto_param" = %(auto_param)s '
        'AND "using_alias" = %(using_alias)s '
        'AND "custom_param" = %(my_param)s'
    )


def test_select_count():
    query = select(Count(star), from_='person', group_by='age')
    assert query == 'SELECT COUNT(*) FROM "person" GROUP BY "age"'


def test_select_join_natural():
    query = select(from_=('person', join.natural('detail')))
    assert query == 'SELECT * FROM "person" NATURAL JOIN "detail"'


def test_select_join_inner_on():
    query = select(from_=('person', join.inner('detail', on={
        'person.person_id': 'detail.person_id',
    })))
    assert query == (
        'SELECT * FROM "person" '
        'INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"'
    )


def test_select_join_left_using():
    query = select(from_=('person', join.left('detail', using='person_id')))
    assert query == """
        SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")
    """.strip()


def test_select_join_cross():
    query = select(from_=('person', join.cross('detail')))
    assert query == 'SELECT * FROM "person" CROSS JOIN "detail"'


def test_select_join_right_using():
    query = select(from_=('person', join.right('detail', using=['person_id'])))
    assert query == """
        SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")
    """.strip()
