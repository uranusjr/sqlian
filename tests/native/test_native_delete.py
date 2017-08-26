from sqlian import Ref, delete


def test_delete():
    query = delete('person', where=(Ref('person_id') == 'mosky'))
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_delete_dict():
    query = delete('person', where={'person_id': 'mosky'})
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
