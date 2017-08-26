from sqlian import update


def test_update():
    query = update(
        'person', set={'name': 'Mosky Liu'},
        where={'person_id': 'mosky'},
    )
    assert query == """
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    """.strip()


def test_update_tuple_set():
    query = update(
        'person', set=('name', 'Mosky Liu'),
        where={'person_id': 'mosky'},
    )
    assert query == """
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    """.strip()


def test_update_tuple_list_set():
    query = update(
        'person', set=[('name', 'Mosky Liu'), ('age', 26)],
        where={'person_id': 'mosky'},
    )
    assert query == (
        """UPDATE "person" SET "name" = 'Mosky Liu', "age" = 26 """
        """WHERE "person_id" = 'mosky'"""
    )
