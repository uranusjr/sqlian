=======
SQLian
=======

.. image:: https://travis-ci.org/uranusjr/sqlian.svg?branch=master
    :target: https://travis-ci.org/uranusjr/sqlian
    :alt: Project Build Status

.. image:: https://readthedocs.org/projects/sqlian/badge/?version=latest
    :target: http://sqlian.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


A good SQLian like a good shepherd. I handle SQL strings so you don’t have to.


Sneak Peek
============

Connect to a database::

    import sqlian
    db = sqlian.connect('postgresql:://user:pa55@localhost/contactbook')


Perform a query::

    rows = db.select(
        'name', 'occupation',
        from_='person',
        where={'main_language': 'Python'},
    )


Access the data directly::

    >>> rows[0]
    <Record {"name": "Mosky", "occupation": "Pinkoi"}>


Or iterate over them::

    for r in rows:
        print('{} works at {}'.format(r.name, r.occupation))


Want more? `Read the documentation. <https://sqlian.readthedocs.io/en/latest/#table-of-contents>`__
