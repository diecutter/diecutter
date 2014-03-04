# -*- coding: utf-8 -*-
"""Utilities that could be packaged in separate project."""
from diecutter.utils import dispatchers
from diecutter.utils.forms import to_boolean
from diecutter.utils.http import accepted_types


__all__ = ['dispatchers',
           'to_boolean',
           'accepted_types']
