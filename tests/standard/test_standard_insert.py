from sqlian import Sql


def test_insert(engine):
    sql = engine.insert(
        'person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'),
    )
    assert sql == Sql(
        '''INSERT INTO "person" ("person_id", "name") '''
        '''VALUES ('mosky', 'Mosky Liu')'''
    )


def test_insert_values(engine):
    sql = engine.insert('person', values=('mosky', 'Mosky Liu'))
    assert sql == Sql('''
        INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')
    '''.strip())


def test_insert_values_multiple(engine):
    sql = engine.insert('person', values=[
        ('mosky', 'Mosky Liu'),
        ('yiyu', 'Yi-Yu Liu'),
    ])
    assert sql == Sql(
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"
    )


def test_insert_dict(engine):
    sql = engine.insert(
        'person', values={'person_id': 'mosky', 'name': 'Mosky Liu'},
    )
    assert sql in (   # Either order works.
        Sql('''INSERT INTO "person" ("person_id", "name") '''
            '''VALUES ('mosky', 'Mosky Liu')'''),

        Sql('''INSERT INTO "person" ("name", "person_id") '''
            '''VALUES ('Mosky Liu', 'mosky')'''),
    )


def test_insert_dict_multiple(engine):
    sql = engine.insert(
        'person', values=[
            {'person_id': 'mosky', 'name': 'Mosky Liu'},
            {'name': 'Yi-Yu Liu', 'person_id': 'yiyu'},
        ],
    )
    assert sql in (   # Either order works.
        Sql('''INSERT INTO "person" ("person_id", "name") '''
            '''VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')'''),

        Sql('''INSERT INTO "person" ("name", "person_id") '''
            '''VALUES ('Mosky Liu', 'mosky'), ('Yi-Yu Liu', 'yiyu')'''),
    )


def test_insert_empty_values(engine):
    sql = engine.insert('person', values=())
    assert sql == Sql('''INSERT INTO "person" VALUES ()''')


def test_insert_empty_values_multiple(engine):
    sql = engine.insert('person', values=[(), (), ()])
    assert sql == Sql("""INSERT INTO "person" VALUES (), (), ()""")
