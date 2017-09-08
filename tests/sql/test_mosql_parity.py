from sqlian import Sql
from sqlian.standard import (
    clauses as c,
    compositions as m,
    constants as n,
    expressions as e,
    functions as f,
    statements as s,
)


def test_delete(engine):
    statement = s.Delete(
        c.DeleteFrom(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), 'mosky')),
    )
    assert statement.__sql__(engine) == Sql('''
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())


def test_insert(engine):
    statement = s.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Columns(m.List(e.Identifier('person_id'), e.Identifier('name'))),
        c.Values(m.List('mosky', 'Mosky Liu')),
    )
    assert statement.__sql__(engine) == Sql(
        """INSERT INTO "person" ("person_id", "name") """
        """VALUES ('mosky', 'Mosky Liu')"""
    )


def test_insert_values(engine):
    statement = s.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(m.List('mosky', 'Mosky Liu')),
    )
    assert statement.__sql__(engine) == Sql('''
        INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')
    '''.strip())


def test_insert_values_multiple(engine):
    statement = s.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(
            m.List('mosky', 'Mosky Liu'),
            m.List('yiyu', 'Yi-Yu Liu'),
        ),
    )
    assert statement.__sql__(engine) == Sql(
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')"
    )


def test_insert_no_values(engine):
    statement = s.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(m.List()),
    )
    assert statement.__sql__(engine) == Sql('''
        INSERT INTO "person" VALUES ()
    '''.strip())


def test_select_where_equal(engine):
    statement = s.Select(
        c.Select(e.Identifier('person_id')),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), 'mosky')),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    '''.strip())


def test_select_where_like(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), 'Mosky%')),
        c.Limit(3), c.Offset(1),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1
    '''.strip())


def test_select_where_in(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.In(
            e.Identifier('person_id'),
            m.List('andy', 'bob'),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')
    '''.strip())


def test_select_where_is_null(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('name'), None)),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "name" IS NULL
    '''.strip())


def test_select_where_greater_than_like(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.And(
            e.GreaterThan(e.Identifier('age'), 20),
            e.Like(e.Identifier('name'), 'Mosky%'),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'
    '''.strip())


def test_select_where_false(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(False),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE FALSE
    '''.strip())


def test_select_from(engine):
    statement = s.Select(c.Select(n.star), c.From(e.Identifier('person')))
    assert statement.__sql__(engine) == Sql('SELECT * FROM "person"')


def test_select_qualified(engine):
    statement = s.Select(
        c.Select(
            e.Identifier('person', 'person_id'),
            e.Identifier('person', 'name'),
        ),
        c.From(e.Identifier('person')),
    )
    assert statement.__sql__(engine) == Sql(
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_as(engine):
    statement = s.Select(
        c.Select(
            m.As(e.Identifier('person', 'person_id'), e.Identifier('id')),
            e.Identifier('person', 'name'),
        ),
        c.From(e.Identifier('person')),
    )
    assert statement.__sql__(engine) == Sql(
        'SELECT "person"."person_id" AS "id", "person"."name" FROM "person"'
    )


def test_select_order_by(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), 'Mosky%')),
        c.OrderBy(e.Identifier('age')),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"
    '''.strip())


def test_select_order_by_desc(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), 'Mosky%')),
        c.OrderBy(m.Ordering(e.Identifier('age'), 'desc')),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    '''.strip())


def test_select_param(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(e.Identifier('table')),
        c.Where(e.And(
            e.Equal(e.Identifier('auto_param'), e.Parameter('auto_param')),
            e.Equal(e.Identifier('using_alias'), e.Parameter('using_alias')),
            e.Equal(e.Identifier('custom_param'), e.Parameter('my_param')),
        )),
    )
    assert statement.__sql__(engine) == Sql(
        'SELECT * FROM "table" '
        'WHERE "auto_param" = %(auto_param)s '
        'AND "using_alias" = %(using_alias)s '
        'AND "custom_param" = %(my_param)s'
    )


def test_select_count(engine):
    statement = s.Select(
        c.Select(f.Count(n.star)),
        c.From(e.Identifier('person')),
        c.GroupBy(e.Identifier('age')),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT COUNT(*) FROM "person" GROUP BY "age"
    '''.strip())


def test_select_join_natural(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(m.Join(
            e.Identifier('person'),
            'NATURAL', e.Identifier('detail'),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" NATURAL JOIN "detail"
    '''.strip())


def test_select_join_inner_on(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(m.Join(
            e.Identifier('person'), 'INNER', e.Identifier('detail'),
            c.On(e.Equal(
                e.Identifier('person', 'person_id'),
                e.Identifier('detail', 'person_id'),
            )),
        )),
    )
    assert statement.__sql__(engine) == Sql(
        'SELECT * FROM "person" '
        'INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"'
    )


def test_select_join_left_using(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(m.Join(
            e.Identifier('person'), 'LEFT', e.Identifier('detail'),
            c.Using(m.List(e.Identifier('person_id'))),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")
    '''.strip())


def test_select_join_cross(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(m.Join(
            e.Identifier('person'),
            'CROSS', e.Identifier('detail'),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" CROSS JOIN "detail"
    '''.strip())


def test_select_join_right_using(engine):
    statement = s.Select(
        c.Select(n.star),
        c.From(m.Join(
            e.Identifier('person'), 'RIGHT', e.Identifier('detail'),
            c.Using(m.List(e.Identifier('person_id'))),
        )),
    )
    assert statement.__sql__(engine) == Sql('''
        SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")
    '''.strip())


def test_update(engine):
    statement = s.Update(
        c.Update(e.Identifier('person')),
        c.Set(m.Assign(e.Identifier('name'), 'Mosky Liu')),
        c.Where(e.Equal(e.Identifier('person_id'), 'mosky')),
    )
    assert statement.__sql__(engine) == Sql('''
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    '''.strip())
