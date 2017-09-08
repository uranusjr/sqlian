from sqlian.standard.engines import Engine as BaseEngine


class Engine(BaseEngine):

    from . import clauses, statements

    def escape_string(self, value):
        if '\0' in value:   # PostgreSQL doesn't handle NULL byte well?
            raise ValueError('null character in string')
        return super(Engine, self).escape_string(value)

    def escape_identifier(self, name):
        if '\0' in name:   # PostgreSQL doesn't handle NULL byte well?
            raise ValueError('null character in identifier')
        return super(Engine, self).escape_identifier(name)
