# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""

#: Mapping between engine name and engines.
#: Used when getting the engine name from the user.
TEMPLATE_ENGINES_MAPPING = {
    'django': 'piecutter.engines.django:DjangoEngine',
    'jinja2': 'piecutter.engines.jinja:Jinja2Engine',
    'filename': 'piecutter.engines.filename:FilenameEngine',
}

#: Default values for settings.
DEFAULTS = {
    'diecutter.service': 'diecutter.local:LocalService',
    'diecutter.engine': 'jinja2',
    'diecutter.filename_engine': 'filename',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in DEFAULTS.items():
        normalized.setdefault(key, value)
    return normalized
