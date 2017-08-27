import pytest

from sqlian import Value, select


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


def test_select_constant():
    query = select(1)
    assert query == 'SELECT 1'


@pytest.mark.xfail(reason='Not auto-wrapping things inside clause.')
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
