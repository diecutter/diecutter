# -*- coding: utf-8 -*-
"""Django template engine."""

from __future__ import absolute_import

from django.conf import settings
settings.configure()
from django.template.loader import render_to_string

from diecutter.engines.base import Engine
from diecutter.exceptions import TemplateError


class DjangoEngine(Engine):
    """Django template engine."""
    def render(self, template, context):
        """Return the rendered template against context."""
        # FIXME: Template syntax error.
        # FIXME: If Django is not installed.
        return render_to_string(template, context)
