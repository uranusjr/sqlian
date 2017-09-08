from sqlian.standard import Database

from .engines import Engine


class MySQLDBDatabase(Database):
    dbapi2_module_name = 'MySQLdb'
    engine_class = Engine


class PyMySQLDatabase(Database):
    dbapi2_module_name = 'pymysql'
    engine_class = Engine
