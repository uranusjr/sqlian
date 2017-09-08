import importlib
import inspect

from sqlian.records import RecordCollection
from sqlian.utils import is_exception_class


class Database(object):

    def __init__(self, **kwargs):
        """__init__(
            self, database,
            host=None, port=None, user=None, password=None,
            params=None, options=None)
        """
        dbapi = self.get_dbapi2()
        self.populate_dbapi2_members(dbapi)
        self._conn = self.create_connection(dbapi, **kwargs)
        self._engine = self.engine_class()

    def __repr__(self):
        return '<Database open={}>'.format(self.is_open())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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

    def create_connection(self, dbapi, **kwargs):
        return dbapi.connect(**kwargs)

    def is_open(self):
        return self._conn is not None

    # DB-API 2.0 interface.

    def close(self):
        self._conn.close()
        self._conn = None

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def cursor(self):
        return self._conn.cursor()

    # Things!

    def execute_statement(self, name, args, kwargs):
        statement = getattr(self._engine, name)(*args, **kwargs)
        cursor = self._conn.cursor()
        cursor.execute(statement)
        return RecordCollection.from_cursor(cursor)

    def select(self, *args, **kwargs):
        return self.execute_statement('select', args, kwargs)

    def insert(self, *args, **kwargs):
        return self.execute_statement('insert', args, kwargs)

    def update(self, *args, **kwargs):
        return self.execute_statement('update', args, kwargs)

    def delete(self, *args, **kwargs):
        return self.execute_statement('delete', args, kwargs)
