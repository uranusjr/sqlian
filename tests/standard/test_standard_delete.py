from sqlian import Sql
from sqlian.standard import Identifier, Equal


def test_delete(engine):
    sql = engine.delete('person', where={'person_id': 'mosky'})
    assert sql == Sql('''
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())


def test_delete_where_list(engine):
    sql = engine.delete('person', where=[
        ('person_id', 'mosky'), ('name', 'Mosky Liu'),
    ])
    assert sql == Sql(
        """DELETE FROM "person" WHERE "person_id" = 'mosky' """
        """AND "name" = 'Mosky Liu'"""
    )


def test_delete_dict(engine):
    sql = engine.delete('person', where={'person_id': 'mosky'})
    assert sql == Sql('''
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())


def test_delete_native_where(engine):
    sql = engine.delete('person', where=Equal(
        Identifier('person_id'), 'mosky',
    ))
    assert sql == Sql('''
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())
