# -*- coding: utf-8 -*-
"""Django template engine."""
from __future__ import absolute_import  # Remove ambiguity of ``import django``

from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError

from diecutter.engines import Engine
from diecutter.exceptions import TemplateError

settings.configure()


class DjangoEngine(Engine):
    """Django template engine."""
    def render(self, template, context):
        """Return the rendered template against context."""
        try:
            return Template(template).render(Context(context))
        except TemplateSyntaxError as e:
            raise TemplateError(e)
