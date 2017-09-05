"""Some complementary constant SQL values.

We generally reuse Python keywords to represent SQL values, None for NULL,
True/False for TRUE/FALSE, etc. But SQL has unique reserved values that do
not exit in Python. They are defined here.
"""


__all__ = ['Constant', 'Star', 'star']


class Constant(object):
    def __repr__(self):
        return '{}()'.format(type(self).__name__)


class Star(Constant):
    pass


star = Star()
