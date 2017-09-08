from sqlian.standard import Database

from .engines import Engine


class Psycopg2Database(Database):
    dbapi2_module_name = 'psycopg2'
    engine_class = Engine
