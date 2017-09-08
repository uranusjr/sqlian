from sqlian import Sql, star


def test_select_locking(engine, c, e, f, s):
    statement = s.Select(
        c.Select(f.Count(star)),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), 1)),
        c.Locking('update', e.Identifier('person'), 'nowait'),
    )
    assert statement.__sql__(engine) == Sql(
        'SELECT COUNT(*) FROM "person" WHERE "person_id" = 1 '
        'FOR UPDATE OF "person" NOWAIT'
    )


def test_insert_returning(engine, c, e, m, s):
    statement = s.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Columns(m.List(e.Identifier('person_id'), e.Identifier('name'))),
        c.Values(m.List('mosky', 'Mosky Liu')),
        c.Returning(star),
    )
    assert statement.__sql__(engine) == Sql(
        'INSERT INTO "person" ("person_id", "name") '
        "VALUES ('mosky', 'Mosky Liu') RETURNING *"
    )
