from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    queries as q,
    values as v,
)


def test_insert():
    query = q.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Columns(m.List(e.Identifier('person_id'), e.Identifier('name'))),
        c.Values(m.List(v.Value('mosky'), v.Value('Mosky Liu'))),
    )
    assert sql(query) == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )


def test_insert_values():
    query = q.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(m.List(v.Value('mosky'), v.Value('Mosky Liu'))),
    )
    assert sql(query) == """
        INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')
    """.strip()


def test_insert_values_multiple():
    query = q.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(
            m.List(v.Value('mosky'), v.Value('Mosky Liu')),
            m.List(v.Value('yiyu'), v.Value('Yi-Yu Liu'))),
    )
    assert sql(query) == (
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"
    )


def test_insert_no_values():
    query = q.Insert(c.InsertInto(e.Identifier('person')), c.Values(m.List()))
    assert sql(query) == """INSERT INTO "person" VALUES ()"""
