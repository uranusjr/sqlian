=======
SQLian
=======

.. image:: https://travis-ci.org/uranusjr/sqlian.svg?branch=master
    :target: https://travis-ci.org/uranusjr/sqlian


A good SQLian like a good shepherd. I handle SQL strings so you don’t have to.


The Basics
============

Connect to a database…

    import sqlian
    db = sqlian.connect('sqlite://:memory:')


Perform a query…

    rows = db.select(
        'name', 'occupation',
        from_='person',
        where={'main_language': 'Python'},
    )


You can access the data directly…

.. code-block:: pycon

    >>> rows[0]
    <Record {"name": "Mosky", "occupation": "Pinkoi"}>


Or iterate over them…

.. code-block:: python

    for r in rows:
        print('{} works at {}'.format(r.name, r.occupation))


And there are much more!
