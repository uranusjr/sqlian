import six


ENGINE_CLASSES = {}


class InvalidScheme(ValueError):

    msg_template = 'can not override scheme {0!r}'

    def __init__(self, *args):
        super(InvalidScheme, self).__init__(self.msg_template.format(*args))


class DuplicateScheme(InvalidScheme):
    msg_template = '{0!r} is already registered to {1!r}'


def register_engine(scheme, klass, exist_ok=False):
    if not exist_ok and scheme in ENGINE_CLASSES:
        raise DuplicateScheme(scheme)
    if scheme in six.moves.urllib.parse.uses_netloc:
        raise InvalidScheme(scheme)
    ENGINE_CLASSES[scheme] = klass
    six.moves.urllib.parse.uses_netloc.append(scheme)


register_engine('sqlite', 'sqlian.sqlite.databases.Database')
