import collections
import importlib
import re

import six


__all__ = ['DuplicateScheme', 'UnrecognizableScheme', 'register', 'connect']


ENGINE_CLASSES = collections.OrderedDict()


class DuplicateScheme(ValueError):
    """Raised when :func:`register`-ing a database under an existing scheme.
    """
    msg_template = '{0!r} is already registered to {1!r}'


class UnrecognizableScheme(ValueError):
    """Raised when trying to :func:`connect` to an unknown scheme.
    """
    def __init__(self, scheme):
        super(UnrecognizableScheme, self).__init__(
            'no matching database for {!r}'.format(scheme),
        )


def register(scheme, klass, replaces_existing=False):
    """Register a database type to be usable by :func:`connect`.

    After registering a database class, it will be instantiatable via
    :func:`connect` by specifying the appropriate scheme.

    :param scheme: The scheme to register this class under.
    :param klass: The database class to register.
    :param replaces_existing: If ``True``, replaces the existing if there is
        already a database registered under this scheme. When ``False``, try
        to prevent this by raising an :class:`DuplicateScheme` error.
    """
    if not replaces_existing and scheme in ENGINE_CLASSES:
        raise DuplicateScheme(scheme, ENGINE_CLASSES[scheme])
    if isinstance(klass, six.string_types):
        module_path, klass_name = klass.rsplit('.', 1)
        klass = getattr(importlib.import_module(module_path), klass_name)
    ENGINE_CLASSES[scheme] = klass
    six.moves.urllib.parse.uses_netloc.append(scheme)


# TODO: These don't actually work yet.

register('mysql', 'sqlian.mysql.MySQLDBDatabase')
register('mysqldb+mysql', 'sqlian.mysql.MySQLDBDatabase')
# register('pymysql+mysql', 'sqlian.mysql.PyMySQLDatabase')

register('postgresql', 'sqlian.postgresql.Psycopg2Database')
register('psycopg2+postgresql', 'sqlian.postgresql.Psycopg2Database')

register('sqlite', 'sqlian.sqlite.SQLite3Database')
register('sqlite3+sqlite', 'sqlian.sqlite.SQLite3Database')


IN_MEMORY_DB_PATTERN = re.compile(r'^(?P<scheme>\w+)://:memory:$')


def connect(url):
    """Create a database connection.

    The database URL takes the form::

        scheme://username:password@host:port/database

    Multiple parts of the form can be omitted if not present. Common examples:

    * ``postgresql:///db`` connects to the local PostgreSQL instance via
      Un*x sockets without authentication, to the database ``db``. Psycopg2,
      the default PostgreSQL driver, is used.
    * ``mysql+pymysql://localhost/db`` connects to the ``db`` database in the
      MySQL instance at localhost, using no authentication. The PyMySQL driver
      is used.
    * ``sqlite:///db.sqlite3`` connects to the SQLite3 file at relative path
      ``db.sqlite3``. The third slash is to seperate path from the host. Use
      four slashes if you need to specify an absolute path. The default driver
      (built-in `sqlite3`) is used.
    """
    # Special case sqlite://:memory: because urlsplit chokes on the colons.
    match = IN_MEMORY_DB_PATTERN.match(url)
    if match:
        scheme = match.group('scheme')
        try:
            engine_class = ENGINE_CLASSES[scheme]
        except KeyError:
            raise UnrecognizableScheme(scheme)
        return engine_class(database=':memory:')

    parts = six.moves.urllib.parse.urlsplit(url)

    try:
        engine_class = ENGINE_CLASSES[parts.scheme]
    except KeyError:
        raise UnrecognizableScheme(parts.scheme)

    database = parts.path
    if database.startswith('/'):
        database = database[1:]

    kwargs = {}
    if parts.hostname:
        kwargs['host'] = parts.hostname
    if parts.port:
        kwargs['port'] = parts.port
    if database:
        kwargs['database'] = database
    if parts.username:
        kwargs['username'] = parts.username
    if parts.password:
        kwargs['password'] = parts.password
    if parts.query:
        # TODO: The result is late-winning when there are duplicate keys.
        # This seems to be a good strategy to me, but *maybe* we should do
        # something when there are duplicate options?
        query_pairs = six.moves.urllib.parse.parse_qsl(parts.query)
        kwargs['options'] = collections.OrderedDict(query_pairs)

    return engine_class(**kwargs)


# HACK: Dynamically generate a list of available engines in the documentation.
connect.__doc__ += """
A list of available schemes:

{}
""".format('\n'.join(
    '* ``{}``'.format(key) for key in ENGINE_CLASSES
))
