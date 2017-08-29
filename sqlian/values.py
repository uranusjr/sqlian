import numbers
import re

import six

from .base import Parsable, Sql, UnescapableError
from .compositions import List
from .utils import is_non_string_sequence, sql_format_string_literal


class Constant(object):

    cache = {}

    def __new__(cls, s):
        if s not in cls.cache:
            cls.cache[s] = super(Constant, cls).__new__(cls)
        return cls.cache[s]

    def __init__(self, s):
        super(Constant, self).__init__()
        self.sql_string = s

    def __repr__(self):
        return 'Constant({})'.format(self.sql_string)

    def __sql__(self):
        return Sql(self.sql_string)


null = Constant('NULL')
star = Constant('*')

true = Constant('TRUE')
false = Constant('FALSE')


class Parameter(object):

    def __init__(self, name):
        super(Parameter, self).__init__()
        self.name = name

    def __repr__(self):
        return '<Param %({})s>'.format(self.name)

    def __sql__(self):
        return Sql('%({})s'.format(self.name))


class Value(Parsable):

    constants = {
        (bool, True): true,
        (bool, False): false,
        (type(None), None): null,
    }

    def __new__(cls, wrapped):
        key = (type(wrapped), wrapped)
        if key in cls.constants:
            return cls.constants[key]
        return super(Value, cls).__new__(cls)

    def __init__(self, wrapped):
        super(Value, self).__init__()
        self.wrapped = wrapped

    def __repr__(self):
        return 'Value({!r})'.format(self.wrapped)

    def __sql__(self):
        if isinstance(self.wrapped, numbers.Number):
            return Sql(self.wrapped)
        if isinstance(self.wrapped, six.binary_type):
            self.wrapped = self.wrapped.decode('utf-8')
        if isinstance(self.wrapped, six.text_type):
            return Sql(sql_format_string_literal(self.wrapped))
        raise UnescapableError(self.wrapped)

    @classmethod
    def parse_native(cls, value):
        if is_non_string_sequence(value):
            return List(*(cls.parse(v) for v in value))
        return super(Value, cls).parse_native(value)
