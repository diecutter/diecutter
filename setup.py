# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

NAME = 'diecutter'
README = open(os.path.join(here, 'README')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
PACKAGES = [NAME]
REQUIREMENTS = ['setuptools',
                'cornice',
                'PasteScript',
                'PasteDeploy',
                'waitress',
                'jinja2',
                'mock',
                'webtest']


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
          version=VERSION,
          description='Templates as a service',
          long_description=README,
          classifiers=['Development Status :: 3 - Alpha',
                       "Programming Language :: Python",
                       "Framework :: Pylons",
                       "Topic :: Internet :: WWW/HTTP",
                       "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                       ],
          keywords="'web services' templates template configuration "
                   "'code generator'",
          author=u'Rémy HUBSCHER',
          author_email='hubscher.remy@gmail.com',
          url='https://github.com/novagile/diecutter',
          packages=PACKAGES,
          include_package_data=True,
          zip_safe=False,
          install_requires=REQUIREMENTS,
          entry_points={'paste.app_factory': ['main = diecutter:main']},
          paster_plugins=['pyramid'])
