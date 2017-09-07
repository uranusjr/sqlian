from sqlian.standard import Database as StandardDatabase

from .engines import Engine


class Database(StandardDatabase):

    engine_class = Engine

    def create_connection(self, database):
        import sqlite3
        return sqlite3.connect(database)
