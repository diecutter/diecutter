# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""

#: Default values for settings.
DEFAULTS = {
    'diecutter.service': 'diecutter.local:LocalService',
    'diecutter.engine': 'jinja2',
    'diecutter.filename_engine': 'filename',
    'diecutter.engine.django': 'piecutter.engines.django:DjangoEngine',
    'diecutter.engine.jinja2': 'piecutter.engines.jinja:Jinja2Engine',
    'diecutter.engine.filename': 'piecutter.engines.filename:FilenameEngine',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in DEFAULTS.items():
        normalized.setdefault(key, value)
    return normalized
