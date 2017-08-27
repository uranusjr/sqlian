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
    assert query in (   # Either order works.
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')""",

        """INSERT INTO "person" ("name", "person_id") """
        """VALUES ('Mosky Liu', 'mosky')""",
    )


def test_insert_dict_multiple():
    query = insert(
        'person', values=[
            {'person_id': 'mosky', 'name': 'Mosky Liu'},
            {'name': 'Yi-Yu Liu', 'person_id': 'yiyu'},
        ],
    )
    assert query in (   # Either order works.
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')""",

        """INSERT INTO "person" ("name", "person_id") """
        """VALUES ('Mosky Liu', 'mosky'), ('Yi-Yu Liu', 'yiyu')""",
    )


def test_insert_empty_values():
    query = insert('person', values=())
    assert query == """INSERT INTO "person" VALUES ()"""


def test_insert_empty_values_multiple():
    query = insert('person', values=[(), (), ()])
    assert query == """INSERT INTO "person" VALUES (), (), ()"""
