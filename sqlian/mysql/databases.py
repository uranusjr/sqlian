from sqlian.standard import Database

from .engines import Engine


class MySQLdbDatabase(Database):
    dbapi2_module_name = 'MySQLdb'
    engine_class = Engine
