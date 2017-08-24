from sqlian import (
    delete,
    expressions as e,
)


def test_delete():
    query = delete('person', where=(e.Ref('person_id') == 'mosky'))
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_delete_dict():
    query = delete('person', where={'person_id': 'mosky'})
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
