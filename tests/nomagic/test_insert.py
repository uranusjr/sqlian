from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    queries as q,
)


def test_insert_mosky():
    query = q.Insert(
        c.InsertInto(e.Ref('person'), e.Ref('person_id'), e.Ref('name')),
        c.Values('mosky', 'Mosky Liu'),
    )
    assert sql(query) == (
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )
