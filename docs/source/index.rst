==========================================
SQLian: handles SQL so you don't need to
==========================================

SQLian is an all-in-one library that "shephards" you through interaction with
SQL. Unlike an ORM (like the ones come with Django, SQLAlchemy, etc.), it does
not try to hide the fact you're writing SQL, but on the other hand still:

* Frees you from handling pesky SQL syntax oddities, so you can better debug
  your SQL like your Python code.
* Provides a unified interface to connect to different database
  implementations.
* Automatic cursor handling anda better way to interact with the data returned
  by the SQL database.


The Basics
============

Connect to a database:

.. code-block:: python

    import sqlian
    db = sqlian.connect('postgresql://...')


and perform a query:

.. code-block:: python

    rows = db.select(
        'name', 'occupation',
        from_='person',
        where={'favorite_language': 'Python'},
    )


Now you can access the data directly:

.. code-block:: pycon

    >>> rows[0]
    <Record {"name": "Mosky", "occupation": "Pinkoi"}>


or iterate over them:

.. code-block:: python

    for r in rows:
        print('{} works at {}'.format(r.name, r.occupation))


Interested? Read on!


.. toctree::
   :maxdepth: 2
   :caption: Contents


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
