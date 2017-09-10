Database Conenctions
====================

.. currentmodule:: sqlian

SQLian provide an interface to connect to relational database backends through
the database API. The main way to do this is by passing a database URL to the
:func:`connect` function, but it is also possible to explicitly create
:class:`Database` instances for various backends.


The Main Interface
------------------

.. autofunction:: connect

.. autoclass:: UnrecognizableScheme

.. autoclass:: Database
    :members:


Connecting to Unsupported Databases
-----------------------------------

To connect to a database not yet supported by SQLian, you need to implement
your own Database subclass, and optionally register it to SQLian if you want
to use it with :func:`connect`.


Implement a Database
~~~~~~~~~~~~~~~~~~~~

Most functionalities are available by subclassing :class:`Database`, but you
need to declare and do a few things to interface with the underlying DB-API
2.0 module:

* Declare `dbapi2_module_name` on the class. This should be a dotted import
  path to the DB-API 2.0 module, i.e. the thing you put after the ``import``
  keyword.
* Declare `engine_class` on the class. This should be :class:`Engine` or its
  subclass. Use the basic :class:`Engine` if your database support the standard
  SQL syntax, and you don't need vendor-specific commands (e.g. MySQL's
  `REPLACE`). See documenttion on engines for detailed explaination on how to
  build custom engine classes.
* Override :meth:`Database.connect` to instruct the class how to call connect
  on the underlying DB-API module.


Register the Database (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use :func:`register` to let :func:`connect` recognize your database's URL
scheme.

.. autofunction:: register

.. autoclass:: DuplicateScheme
