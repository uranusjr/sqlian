from sqlian.standard import Database

from .engines import Engine


class Psycopg2Database(Database):
    dbapi2_module_name = 'psycopg2'
    engine_class = Engine


class PyPostgreSQLDatabase(Database):
    dbapi2_module_name = 'postgresql.driver.dbapi20'
    engine_class = Engine
