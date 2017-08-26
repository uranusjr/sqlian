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
