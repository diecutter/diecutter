"""Stuff related to server."""
from pyramid.config import Configurator


def main(global_config, **settings):
    """Return WSGI application using ``global_config`` and ``settings``."""
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("diecutter.views")
    return config.make_wsgi_app()
