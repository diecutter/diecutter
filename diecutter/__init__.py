"""Main entry point
"""
from pyramid.config import Configurator

pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('diecutter')

#: Module version, as defined in PEP-0396.
__version__ = distribution.version


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("diecutter.views")
    return config.make_wsgi_app()
