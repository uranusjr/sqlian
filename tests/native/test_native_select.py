from sqlian import select


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
    assert query == """
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'
    """.strip()


def test_select_where_false():
    query = select(from_='person', where=False)
    assert query == 'SELECT * FROM "person" WHERE FALSE'


def test_select_from():
    query = select(from_='person')
    assert query == 'SELECT * FROM "person"'


def test_select_constant():
    query = select(1)
    assert query == 'SELECT 1'
