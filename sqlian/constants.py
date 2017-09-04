class Constant(object):
    def __repr__(self):
        return '{}()'.format(type(self).__name__)


class Star(Constant):
    pass


star = Star()
