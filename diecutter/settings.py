# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""

#: Default values for settings.
defaults = {
    'diecutter.service': 'diecutter.local:LocalService',
    'diecutter.template_engine': 'diecutter.engines.jinja:Jinja2Engine',
    'diecutter.filename_template_engine': 'diecutter.engines.filename'
                                          ':FilenameEngine',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in defaults.items():
        normalized.setdefault(key, value)
    return normalized
