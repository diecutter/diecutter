# -*- coding: utf-8 -*-
from jinja2 import Template
from jinja2.exceptions import UndefinedError, TemplateSyntaxError
from diecutter.exceptions import TemplateError


class Jinja2Engine(object):
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

engine = Jinja2Engine()
