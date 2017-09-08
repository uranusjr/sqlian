import collections
import functools
import inspect
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


def is_exception_class(obj):
    return inspect.isclass(obj) and issubclass(obj, Exception)


def is_flat_tuple(s):
    return (
        isinstance(s, tuple) and
        all(not is_non_string_sequence(v) for v in s)
    )


def is_flat_two_tuple(s):
    return (
        isinstance(s, tuple) and
        len(s) == 2 and
        all(not is_non_string_sequence(v) for v in s)
    )


def is_non_string_sequence(s):
    return (
        isinstance(s, collections.Sequence) and
        not isinstance(s, six.string_types)
    )


def is_partial_of(s, func):
    return isinstance(s, functools.partial) and s.func is func


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
