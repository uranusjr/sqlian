import collections
import itertools

import six


def partition(predicate, iterable):
    """Use `predicate` to partition entries into falsy and truthy ones.

    Recipe taken from the official documentation.
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    t1, t2 = itertools.tee(iterable)
    return (
        six.moves.filterfalse(predicate, t1),
        six.moves.filter(predicate, t2),
    )


def sql_format_string_literal(value):
    # SQL standard: replace single quotes with pairs of them.
    value = value.replace("'", "''")
    if '\0' in value:   # TODO: Is there a good way to handle this?
        raise ValueError('null character in string')
    return "'{}'".format(value)


def sql_format_identifier(name):
    # TODO: Escape special characters?
    return '"{}"'.format(name)


def is_non_string_sequence(s):
    return (
        isinstance(s, collections.Sequence) and
        not isinstance(s, six.string_types)
    )


def is_single_row(iterable):
    return (
        getattr(iterable, '__single_row__', False) or
        any(not is_non_string_sequence(v) for v in iterable)
    )


def is_values_mapping_sequence(s):
    """Check if `s` is a native VALUES mapping sequence.

    A variable is a VALUES mapping sequence if it is a sequence of mappings,
    and all mappings in it have the same keys.
    """
    return (
        isinstance(s, collections.Sequence) and
        all(isinstance(d, collections.Mapping) for d in s) and
        len({frozenset(d.keys()) for d in s}) == 1
    )


class NativeRow(six.moves.UserList):
    """A list that explicits represents a single row, not a sequence of rows.

    This acts like a normal list, but sets an explicit marker to indicate it
    is a single row, to disable the auto-parsing functionality.
    """
    __single_row__ = True
