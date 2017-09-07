from sqlian.records import RecordCollection


class Database(object):

    def __init__(self, **kwargs):
        """__init__(
            self, database,
            host=None, port=None, user=None, password=None,
            params=None, options=None)
        """
        self._conn = self.create_connection(**kwargs)
        self._engine = self.engine_class()
        self._open = True

    def __repr__(self):
        return '<Database open={}>'.format(self.is_open())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_connection(self, **kwargs):
        raise NotImplementedError(
            'implement connect to return a DB-API connection instance',
        )

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

    def perform_query(self, name, args, kwargs):
        query = getattr(self._engine, name)(*args, **kwargs)
        cursor = self._conn.cursor()
        cursor.execute(query)
        return RecordCollection.from_cursor(cursor)

    def select(self, *args, **kwargs):
        return self.perform_query('select', args, kwargs)

    def insert(self, *args, **kwargs):
        return self.perform_query('insert', args, kwargs)

    def update(self, *args, **kwargs):
        return self.perform_query('update', args, kwargs)

    def delete(self, *args, **kwargs):
        return self.perform_query('delete', args, kwargs)
