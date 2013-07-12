# -*- coding: utf-8 -*-
"""WSGI integration."""
import os

from pyramid.config import Configurator
from pyramid.paster import get_app, setup_logging
from pyramid.path import DottedNameResolver

import diecutter.settings


def for_modwsgi(settings_file, virtualenv_dir):
    """Return WSGI application for use with mod_wsgi."""
    activate_this = os.path.join(virtualenv_dir, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))
    return for_file(settings_file)


def for_file(settings_file):
    """Return WSGI application using settings file."""
    setup_logging(settings_file)
    return get_app(settings_file, 'main')


def for_paste(global_config, **settings):
    """Return WSGI application using ``global_config`` and ``settings``."""
    settings = diecutter.settings.normalize(settings)
    config = Configurator(settings=settings)
    service_factory_path = settings['diecutter.service']
    service_factory = DottedNameResolver().resolve(service_factory_path)
    service = service_factory()
    config.include("cornice")  # Diecutter uses Cornice.
    diecutter.views.register_service(config, 'diecutter', service, '/')
    return config.make_wsgi_app()
