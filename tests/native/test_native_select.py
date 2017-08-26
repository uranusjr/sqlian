from sqlian import select


def test_select_where_equal():
    query = select('person_id', from_='person', where={'person_id': 'mosky'})
    assert query == """
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
