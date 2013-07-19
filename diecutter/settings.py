# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""

#: Mapping between engine name and engines.
#: Used when getting the engine name from the user.
TEMPLATE_ENGINES_MAPPING = {
    'django': 'diecutter.engines.django:DjangoEngine',
    'jinja2': 'diecutter.engines.jinja:Jinja2Engine',
    'filename': 'diecutter.engines.filename:FilenameEngine',
}

#: Default values for settings.
DEFAULTS = {
    'diecutter.service': 'diecutter.local:LocalService',
    'diecutter.template_engine': 'diecutter.engines.jinja:Jinja2Engine',
    'diecutter.filename_template_engine':
    'diecutter.engines.filename:FilenameEngine',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in DEFAULTS.items():
        normalized.setdefault(key, value)
    return normalized
