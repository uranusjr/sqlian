#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


def get_version():
    code = None
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sqlian',
        '__init__.py',
    )
    with open(path) as f:
        for line in f:
            if line.startswith('VERSION'):
                code = line[len('VERSION = '):]
                break
    return '.'.join(str(v) for v in eval(code))


readme = open('README.rst').read()
# history = open('HISTORY.rst').read().replace('.. :changelog:', '')
history = ''


setup(
    name='sqlian',
    version=get_version(),
    description='A good SQLian like a good shepherd.',
    long_description='\n\n'.join([readme, history]),
    author='Tzu-ping Chung',
    author_email='uranusjr@gmail.com',
    url='https://github.com/uranusjr/sqlian',
    packages=find_packages(),
    install_requires=['six'],
    license='ISC',
    keywords='SQL',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: SQL',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
