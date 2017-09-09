import importlib
import inspect

from sqlian.records import RecordCollection
from sqlian.utils import is_exception_class


class Database(object):
    """A database connection.

    This class provides a wrapper to a `DB-API 2.0`_ Connection instance,
    offering additional SQL-building methods alongside with the standard API.

    Keyord arguments passed to the constructor are used to create the
    underlying `Connection` instance. See documentation of the underlying
    DB-API 2.0 module for appropriate parameters to pass.

    Instances of this class implement the context manager interface. The
    instance itself is assigned to the **as** expression, and the connection
    is closed when the context manager exists, committing done automatically
    if there are no exceptions.

    .. _`DB-API 2.0`: https://www.python.org/dev/peps/pep-0249
    """
    def __init__(self, **kwargs):
        # Typical signature:
        # __init__(
        #   self, database, host=None, port=None, user=None, password=None,
        #   params=None, options=None)
        self._conn = self.create_connection(**kwargs)
        self.engine = self.engine_class()

    def __repr__(self):
        return '<Database open={}>'.format(self.is_open())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        self.close()

    @property
    def connection(self):
        """The underlying connection object. This property is read-only.

        :returns: A DB-API 2.0 Connection object.
        """
        return self._conn

    def get_dbapi2(self):
        return importlib.import_module(self.dbapi2_module_name)

    def populate_dbapi2_members(self, dbapi):
        try:
            all_names = set(dbapi.__all__)
        except AttributeError:
            all_names = None
        for name, member in inspect.getmembers(dbapi, is_exception_class):
            if all_names is None or name in all_names:
                setattr(self, name, member)

    def create_connection(self, **kwargs):
        """Creates a connection.

        If you're implementing a wrapper not conforming to DB-API 2.0, you
        should implement this method to override the default behavior, which
        depends on the API.

        Keyword arguments to this method are passed directly from the class
        constructor.

        :returns: A DB-API 2.0 interface object.
        """
        dbapi = self.get_dbapi2()
        self.populate_dbapi2_members(dbapi)
        return dbapi.connect(**kwargs)

    def is_open(self):
        """Whether the connection is open.

        :rtype: bool
        """
        return self._conn is not None

    # DB-API 2.0 interface.

    def close(self):
        """Close the connection.

        This method exists to conform to DB-API 2.0.
        """
        self._conn.close()
        self._conn = None

    def commit(self):
        """Commit any pending transaction to the database.

        This method exists to conform to DB-API 2.0.
        """
        self._conn.commit()

    def rollback(self):
        """Rollback pending transaction.

        This method exists to conform to DB-API 2.0. Behavior of calling this
        method on a database not supporting transactions is undefined.
        """
        self._conn.rollback()

    def cursor(self):
        """Return a new Cursor Object using the connection.

        This method exists to conform to DB-API 2.0.
        """
        return self._conn.cursor()

    # Things!

    def execute_statement(self, statement, args, kwargs):
        """Build a statement, and execute it on the connection.

        :rtype: RecordCollection
        """
        cursor = self._conn.cursor()
        cursor.execute(statement)
        return RecordCollection.from_cursor(cursor)

    def select(self, *args, **kwargs):
        """Build and execute a SELECT statement.
        """
        return self.execute_statement(self.engine.select, args, kwargs)

    def insert(self, *args, **kwargs):
        """Build and execute an INSERT statement.
        """
        return self.execute_statement(self.engine.insert, args, kwargs)

    def update(self, *args, **kwargs):
        """Build and execute an UPDATE statement.
        """
        return self.execute_statement(self.engine.update, args, kwargs)

    def delete(self, *args, **kwargs):
        """Build and execute a DELETE statement.
        """
        return self.execute_statement(self.engine.delete, args, kwargs)
