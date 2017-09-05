from sqlian.standard.engines import Engine as BaseEngine


class Engine(BaseEngine):

    def escape_string(self, value):
        if '\0' in value:   # SQLite doesn't handle NULL byte well?
            raise ValueError('null character in string')
        return super(Engine, self).escape_string(value)

    def escape_identifier(self, name):
        if '\0' in name:   # SQLite doesn't handle NULL byte well?
            raise ValueError('null character in identifier')
        return super(Engine, self).escape_identifier(name)
