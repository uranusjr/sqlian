from sqlian import Identifier, delete


def test_delete():
    query = delete('person', where=('person_id', 'mosky'))
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_delete_where_list():
    query = delete(
        'person',
        where=[('person_id', 'mosky'), ('name', 'Mosky Liu')],
    )
    assert query == (
        """DELETE FROM "person" WHERE "person_id" = 'mosky' """
        """AND "name" = 'Mosky Liu'"""
    )


def test_delete_dict():
    query = delete('person', where={'person_id': 'mosky'})
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_delete_native_where():
    query = delete('person', where=(Identifier('person_id') == 'mosky'))
    assert query == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
