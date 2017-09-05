from sqlian import Sql, star


def test_select_for_update(engine, c, e, f, q):
    sql = q.Select(
        c.Select(f.Count(star)),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), 1)),
        c.ForUpdate(),
    )
    assert sql.__sql__(engine) == Sql('''
        SELECT COUNT(*) FROM `person` WHERE `person_id` = 1 FOR UPDATE
    '''.strip())


def test_select_lock_in_share_mode(engine, c, e, q):
    sql = q.Select(
        c.Select(star),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), 1)),
        c.LockInShareMode(),
    )
    assert sql.__sql__(engine) == Sql(
        'SELECT * FROM `person` WHERE `person_id` = 1 LOCK IN SHARE MODE'
    )


def test_insert_on_duplicate_key_update(engine, c, e, m, q):
    sql = q.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(m.List('mosky', 'Mosky Liu')),
        c.OnDuplicateKeyUpdate(m.Assign(e.Identifier('name'), 'Mosky Liu')),
    )
    assert sql.__sql__(engine) == Sql(
        'INSERT INTO `person` '
        "VALUES ('mosky', 'Mosky Liu') "
        """ON DUPLICATE KEY UPDATE `name` = 'Mosky Liu'"""
    )


def test_replace(engine, c, e, m, q):
    sql = q.Replace(
        c.ReplaceInto(e.Identifier('person')),
        c.Columns(m.List(e.Identifier('person_id'), e.Identifier('name'))),
        c.Values(m.List('mosky', 'Mosky Liu')),
    )
    assert sql.__sql__(engine) == Sql(
        'REPLACE INTO `person` (`person_id`, `name`) '
        "VALUES ('mosky', 'Mosky Liu')"
    )
