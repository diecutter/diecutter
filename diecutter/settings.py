# -*- coding: utf-8 -*-
"""Parse settings, set defaults."""

#: Default values for settings.
defaults = {
    'diecutter.service': 'diecutter.views.LocalService',
}


def normalize(settings={}):
    """Return a copy of settings dictionary with normalized values.

    Sets default values if necessary.

    """
    normalized = settings.copy()
    for key, value in defaults.items():
        normalized.setdefault(key, value)
    return normalized
