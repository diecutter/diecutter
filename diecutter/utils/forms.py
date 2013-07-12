# -*- coding: utf-8 -*-
"""Forms and data validation."""


def to_boolean(value):
    """Convert ``value`` string to boolean.

    >>> from diecutter.utils.forms import to_boolean
    >>> to_boolean('1')
    True
    >>> to_boolean('0')
    False
    >>> to_boolean('yes')
    True
    >>> to_boolean('no')
    False

    """
    _BOOL_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                    '0': False, 'no': False, 'false': False, 'off': False}

    value = str(value).lower().strip()
    if value not in _BOOL_STATES:
        raise ValueError(value)
    return _BOOL_STATES[value]
