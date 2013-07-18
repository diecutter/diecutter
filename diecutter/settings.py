# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""
from diecutter.engines.django import DjangoEngine
from diecutter.engines.jinja import Jinja2Engine
from diecutter.engines.filename import FilenameEngine

#: Mapping between engine name and engines
TEMPLATE_ENGINE_MAPPINGS = {
    'django': DjangoEngine,
    'jinja': Jinja2Engine,
    'filename': FilenameEngine,
}

#: Default values for settings.
defaults = {
    'diecutter.service': 'diecutter.local:LocalService',
    'diecutter.template_engine': 'jinja',
    'diecutter.filename_template_engine': 'filename',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in defaults.items():
        normalized.setdefault(key, value)
    return normalized
