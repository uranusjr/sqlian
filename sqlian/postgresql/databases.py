from sqlian import compat
from sqlian.standard import Database

from .engines import Engine


class Psycopg2Database(Database):

    dbapi2_module_name = 'psycopg2'
    engine_class = Engine

    def connect(self, dbapi, **kwargs):
        with compat.suppress(KeyError):
            kwargs['dbname'] = kwargs.pop('database')
        # See libpq documentation for a list of valid parameter key words.
        # We don't enforece anything here; the user should be responsible
        # for whatever is passed in here.
        # https://www.postgresql.org/docs/current/static/libpq-connect.html
        with compat.suppress(KeyError):
            kwargs.update(kwargs.pop('options'))
        return dbapi.connect(**kwargs)
