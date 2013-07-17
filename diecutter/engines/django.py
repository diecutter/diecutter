# -*- coding: utf-8 -*-
"""Django template engine."""
# if we don't do that, the imports from Django fails
# because our file is also called django.py
from __future__ import absolute_import 

from django.template import Template, Context, TemplateSyntaxError
from django.conf import settings

from diecutter.engines.base import Engine
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
