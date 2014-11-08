#!/usr/bin/env python
"""
Based entirely on Django's own ``setup.py``.
"""
from setuptools import setup, find_packages

from tagging.version import __version__


setup(
    name = 'django-tagging',
    version = __version__,
    description = 'Generic tagging application for Django',
    author = 'Jonathan Buchanan',
    author_email = 'jonathan.buchanan@gmail.com',
    url = 'http://code.google.com/p/django-tagging/',
    requires=[
        'django (>=1.3)',
    ],
    packages = find_packages(),
    include_package_data=True,
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
