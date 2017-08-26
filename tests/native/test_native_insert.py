from sqlian import insert


def test_insert():
    query = insert(
        'person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'),
    )
    assert query == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )


def test_insert_values():
    query = insert('person', values=('mosky', 'Mosky Liu'))
    assert query == """
        INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')
    """.strip()


def test_insert_values_multiple():
    query = insert('person', values=[
        ('mosky', 'Mosky Liu'),
        ('yiyu', 'Yi-Yu Liu'),
    ])
    assert query == (
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"
    )


def test_insert_dict():
    query = insert(
        'person', values={'person_id': 'mosky', 'name': 'Mosky Liu'},
    )
    assert query == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )


def test_insert_dict_multiple():
    query = insert(
        'person', values=[
            {'person_id': 'mosky', 'name': 'Mosky Liu'},
            {'name': 'Yi-Yu Liu', 'person_id': 'yiyu'},
        ],
    )
    assert query == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"""
    )


def test_insert_no_values():
    query = insert('person', values=())
    assert query == """INSERT INTO "person" VALUES ()"""


def test_insert_no_values_multiple():
    query = insert('person', values=[(), (), ()])
    assert query == """INSERT INTO "person" VALUES (), (), ()"""
