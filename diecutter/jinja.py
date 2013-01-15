# -*- coding: utf-8 -*-
from jinja2 import Template
from jinja2.exceptions import UndefinedError
from diecutter.exceptions import TemplateError


class Jinja2Engine(object):
    def render(self, template, context):
        """Return the rendered template against context."""
        template = Template(template)
        try:
            return template.render(**context)
        except UndefinedError as e:
            raise TemplateError(e)

engine = Jinja2Engine()
