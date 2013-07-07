"""Stuff related to server."""
from pyramid.config import Configurator

import diecutter.views
import diecutter.github


def main(global_config, **settings):
    """Return WSGI application using ``global_config`` and ``settings``."""
    config = Configurator(settings=settings)
    config.include("cornice")
    #local_service = diecutter.views.LocalService()
    #diecutter.views.register_service(config, 'diecutter', local_service, '/')
    github_service = diecutter.github.GithubService()
    diecutter.views.register_service(
        config, 'diecutter', github_service, '/')
    return config.make_wsgi_app()
