# -*- coding: utf-8 -*-
"""Jinja2 template engine."""
from jinja2 import Template
from jinja2.exceptions import UndefinedError, TemplateSyntaxError

from diecutter.engines import Engine
from diecutter.exceptions import TemplateError


class Jinja2Engine(Engine):
    """Jinja2 template engine."""
    def render(self, template, context):
        """Return the rendered template against context."""
        try:
            template = Template(template)
        except TemplateSyntaxError as e:
            raise TemplateError(e)
        try:
            return template.render(**context)
        except (UndefinedError, TypeError) as e:
            raise TemplateError(e)
