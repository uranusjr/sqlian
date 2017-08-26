from sqlian import (
    sql,
    base as b,
    clauses as c,
    compositions as m,
    expressions as e,
    queries as q,
)


def test_insert():
    query = q.Insert(
        c.InsertInto(e.Ref('person')),
        c.Columns(m.List(e.Ref('person_id'), e.Ref('name'))),
        c.Values(m.List(b.Value('mosky'), b.Value('Mosky Liu'))),
    )
    assert sql(query) == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )


def test_insert_values():
    query = q.Insert(
        c.InsertInto(e.Ref('person')),
        c.Values(m.List(b.Value('mosky'), b.Value('Mosky Liu'))),
    )
    assert sql(query) == """
        INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')
    """.strip()


def test_insert_values_multiple():
    query = q.Insert(
        c.InsertInto(e.Ref('person')),
        c.Values(
            m.List(b.Value('mosky'), b.Value('Mosky Liu')),
            m.List(b.Value('yiyu'), b.Value('Yi-Yu Liu'))),
    )
    assert sql(query) == (
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"
    )


def test_insert_no_values():
    query = q.Insert(c.InsertInto(e.Ref('person')), c.Values(m.List()))
    assert sql(query) == """INSERT INTO "person" VALUES ()"""
