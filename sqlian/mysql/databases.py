from sqlian import compat
from sqlian.standard import Database
from sqlian.utils import parse_boolean

from .engines import Engine


def noop(value):
    return value


class MySQLDBDatabase(Database):

    dbapi2_module_name = 'MySQLdb'
    engine_class = Engine
    option_converters = {
        'connect_timeout': int,
        'use_unicode': parse_boolean,
    }

    def connect(self, dbapi, **kwargs):
        with compat.suppress(KeyError):
            kwargs['passwd'] = kwargs.pop('password')
        with compat.suppress(KeyError):
            kwargs['db'] = kwargs.pop('database')

        # See MySQL-Python documentation for a list of valid parameters.
        # We don't enforece anything; the user should be responsible for
        # whatever is passed in.
        # http://mysql-python.sourceforge.net/MySQLdb.html
        with compat.suppress(KeyError):
            options = kwargs.pop('options')
            kwargs.update({
                key: self.option_converters.get(key, noop)(value)
                for key, value in options.items()
            })
        return dbapi.connect(**kwargs)


class PyMySQLDatabase(Database):
    dbapi2_module_name = 'pymysql'
    engine_class = Engine
