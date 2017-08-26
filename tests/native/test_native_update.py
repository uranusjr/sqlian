from sqlian import update


def test_update():
    query = update(
        'person', set={'name': 'Mosky Liu'},
        where={'person_id': 'mosky'},
    )
    assert query == """
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    """.strip()
