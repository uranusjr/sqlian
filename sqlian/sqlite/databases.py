from sqlian.standard import Database

from .engines import Engine


class SQLite3Database(Database):

    dbapi2_module_name = 'sqlite3'
    engine_class = Engine

    def connect(self, dbapi, database, **kwargs):
        return dbapi.connect(database)
