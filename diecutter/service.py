"""Stuff related to server."""
from pyramid.config import Configurator
from pyramid.path import DottedNameResolver

import diecutter.views
import diecutter.github


DEFAULT_SERVICE_FACTORY = 'diecutter.views.LocalService'


def main(global_config, **settings):
    """Return WSGI application using ``global_config`` and ``settings``."""
    config = Configurator(settings=settings)
    try:
        service_factory_name = settings['diecutter.service']
    except KeyError:
        service_factory_name = DEFAULT_SERVICE_FACTORY
    service_factory = DottedNameResolver().resolve(service_factory_name)
    service = service_factory()
    config.include("cornice")  # Diecutter uses Cornice.
    diecutter.views.register_service(config, 'diecutter', service, '/')
    return config.make_wsgi_app()
