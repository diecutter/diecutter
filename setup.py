# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()


setup(name='diecutter',
      version=version,
      description='diecutter',
      long_description=README,
      classifiers=["Programming Language :: Python",
                   "Framework :: Pylons",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                   ],
      keywords="web services, templates, template",
      author=u'Rémy HUBSCHER',
      author_email='hubscher.remy@gmail.com',
      url='https://github.com/novagile/diecutter',
      packages=['diecutter'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['cornice', 'PasteScript', 'waitress', 'jinja2'],
      entry_points={'paste.app_factory': ['main = diecutter:main']},
      paster_plugins=['pyramid'],
      )
