from sqlian import Sql


def test_update(engine):
    sql = engine.update(
        'person', set={'name': 'Mosky Liu'},
        where={'person_id': 'mosky'},
    )
    assert sql == Sql('''
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    '''.strip())


def test_update_tuple_set(engine):
    sql = engine.update(
        'person', set=('name', 'Mosky Liu'),
        where={'person_id': 'mosky'},
    )
    assert sql == Sql('''
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    '''.strip())


def test_update_tuple_list_set(engine):
    sql = engine.update(
        'person', set=[('name', 'Mosky Liu'), ('age', 26)],
        where={'person_id': 'mosky'},
    )
    assert sql == Sql(
        """UPDATE "person" SET "name" = 'Mosky Liu', "age" = 26 """
        """WHERE "person_id" = 'mosky'"""
    )
