Installation Guide
===================

I highly recommend you check out Pipenv by Kenneth Reitz to handle you project
dependencies. With Pipenv, you can insall SQLian simply with::

    $ pipenv install sqlian

The "non-modern" way to install SQLian is from the PyPI, through Pip::

    $ pip install sqlian

The source code is also available at GitHub. You can download release packages
directly on it, or use Pip and Git to install the in-development snapshot::

    $ pip install git+https://github.com/uranusjr/sqlian.git

Or even just clone and install manually yourself::

    $ git clone https://github.com/uranusjr/sqlian.git
    $ cd sqlian
    $ python setup.py install
