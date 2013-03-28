# -*- coding: utf-8 -*-
"""Jinja2 template engine."""
from jinja2 import Environment
from jinja2.exceptions import UndefinedError, TemplateSyntaxError

from diecutter.engines import Engine
from diecutter.exceptions import TemplateError


class Jinja2Engine(Engine):
    """Jinja2 template engine."""
    def __init__(self, environment=None):
        if environment is None:
            environment = Environment()
        self.environment = environment

    def render(self, template, context):
        """Return the rendered template against context."""
        try:
            template = self.environment.from_string(template)
        except TemplateSyntaxError as e:
            raise TemplateError(e)
        try:
            return template.render(**context)
        except (UndefinedError, TypeError) as e:
            raise TemplateError(e)
