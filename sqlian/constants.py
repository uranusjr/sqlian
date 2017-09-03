class Constant(object):

    def __init__(self, representation):
        self.representation = representation

    def __repr__(self):
        return 'Const({!r})'.format(self.representation)


star = Constant('*')
