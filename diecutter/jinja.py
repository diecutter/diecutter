# -*- coding: utf-8 -*-
from jinja2 import Template


class Jinja2Engine(object):
    def render(self, template, context):
        """Return the rendered template against context."""
        template = Template(template)
        return template.render(**context)

engine = Jinja2Engine()
