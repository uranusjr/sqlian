.. currentmodule:: sqlian


Quickstart
===========

SQLian is composed of three main parts:

* **Databases** represent database connections.
* **Statement builders** take native objects and convert them to a SQL command
  string. The built command are then passed to the associated database
  connection to be executed.
* **Records** are returned by database queries. They offer a clean, nice
  interface to interact with the data retrieved from the database.

Let's do a quick walk through on them one by one.


Connecting to a database
-------------------------

SQLian uses the 12factor_-inspired database URL syntax to describe a
database. This syntax is compatible with popular tools, including
DJ-Database-URL_, SQLAlchemy_, and everything that builds on top of them.
Which means, like, everything?

As an example, let's connect to a PostgreSQL database:

.. code-block:: python

    import sqlian
    db = sqlian.connect('postgresql://user:pa55@localhost/contactbook')

SQLian has some database support built-in. Some databases require extra
dependencies to actually connect to, like ``psycopg2`` for PostgreSQL. You
can also build your own database support, but we'll save that discussion for
later.

The `connect()` function returns a :class:`Database` instance, which
conforms to the DB-API 2.0 specification (`PEP 249`_), so you can get to work
directly if you know your way around. But there's a better way to do it.


Issuing commands
-----------------

The :class:`Database` instance provides a rich set of "statement builders" that
format and execute SQL for you, and make it easier to convert native Python
objects for SQL usage.

Inserting data:

.. code-block:: python

    db.insert('person', values={
        'name': 'Mosky',
        'occupation': 'Pinkoi',
        'main_language': 'Python',
    })

This roughly translates to:

.. code-block:: sql

    INSERT INTO "person" ("name", "occupation", "main_language")
    VALUES ('Mosky', 'Pinkoi', 'Python')

but saves you from dealing with column and value clauses and all those
``%(name)s`` stuff.

You can still use column name–value sequences if you wish to:

.. code-block:: python

    db.insert(
        'person',
        columns=('name', 'occupation', 'main_language'),
        values=[
            ('Tim', 'GilaCloud', 'Python'),
            ('Adam', 'Pinkoi', 'JavaScript'),
        ],
    )

Did I mention you can insert multiple rows at one go? Yeah, you can.

It's also easy to update data:

.. code-block:: python

    db.update('person', where={'name': 'Adam'}, set={'main_language': 'CSS'})

Notice the key ordering does not matter.

You'd guess how deletion works by now, so let's add a little twist:

.. code-block:: python

    db.delete('person', where={'occupation !=': 'Pinkoi'})

The builders automatically parse trailing operators and do the right thing.


Handling results
-----------------

Some statements produce data. For every such query, SQLian returns an iterable
object :class:`RecordCollection` so you can handle them.

.. code-block:: pycon

    >>> rows = db.select(sqlian.star, from_='person')
    >>> rows
    <RecordCollection (pending)>

Accessing the content in any way automatically resolves it:

.. code-block:: pycon

    >>> rows[0]
    <Record {"name": "Mosky", "occupation": "Pinkoi", "main_language": "Python"}>
    >>> rows
    <RecordCollection (1+ rows, pending)>

.. code-block:: pycon

    >>> for row in rows:
    ...     print(row)
    <Record {"name": "Mosky", "occupation": "Pinkoi", "main_language": "Python"}>
    <Record {"name": "Adam", "occupation": "Pinkoi", "main_language": "CSS"}>
    >>> rows
    <RecordCollection (2 rows)>

A :class:`Record` can be accessed like a sequence, mapping, or even object:

.. code-block:: pycon

    >>> row = rows[0]
    >>> row[0]
    'Mosky'
    >>> row['occupation']
    Pinkoi
    >>> row.main_language
    Python


.. _12factor: https://www.12factor.net/backing-services
.. _DJ-Database-URL: https://github.com/kennethreitz/dj-database-url
.. _SQLAlchemy: https://www.sqlalchemy.org
.. _`PEP 249`: https://www.python.org/dev/peps/pep-0249/
.. _`Sequence and Mapping ABCs`: https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes
