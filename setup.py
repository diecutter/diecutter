# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

NAME = 'diecutter'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
PACKAGES = [NAME]
REQUIREMENTS = ['setuptools',
                'cornice',
                'PasteScript',
                'PasteDeploy',
                'waitress',
                'django',
                'Jinja2',
                'mock',
                'piecutter',
                'requests',
                'webtest']


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
          version=VERSION,
          description='Templates as a service',
          long_description=README,
          classifiers=['Development Status :: 3 - Alpha',
                       "Programming Language :: Python :: 2.7",
                       "Framework :: Pylons",
                       "Topic :: Internet :: WWW/HTTP",
                       "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                       ],
          keywords="'web services' templates template configuration "
                   "'code generator'",
          author=u'Rémy HUBSCHER',
          author_email='hubscher.remy@gmail.com',
          url='https://github.com/diecutter/diecutter',
          packages=PACKAGES,
          include_package_data=True,
          zip_safe=False,
          setup_requires=['PasteScript'],
          install_requires=REQUIREMENTS,
          entry_points={
              'paste.app_factory': ['main = diecutter.wsgi:for_paste'],
          },
          paster_plugins=['pyramid'])
