# -*- coding: utf-8 -*-
"""Tests around diecutter.engines.jinja."""
import unittest

from diecutter.engines.jinja import Jinja2Engine
from diecutter.exceptions import TemplateError


class Jinja2TestCase(unittest.TestCase):
    """Test diecutter.engines.jinja.Jinja2Engine."""
    def test_environment(self):
        """Jinja2Engine's environment contains additional functions."""
        engine = Jinja2Engine()
        environment = engine.environment
        self.assertIn('path_join', environment.globals)
        self.assertIn('path_normalize', environment.globals)

    def test_render_noop(self):
        """Jinja2Engine correctly renders ``Hello world!`` template."""
        engine = Jinja2Engine()
        rendered = engine.render(u'Hello world!', {})
        self.assertEqual(rendered, u'Hello world!')

    def test_render_simple(self):
        """Jinja2Engine correctly renders ``Hello {{ name }}!`` template."""
        engine = Jinja2Engine()
        rendered = engine.render(u'Hello {{ name }}!', {'name': 'world'})
        self.assertEqual(rendered, u'Hello world!')

    def test_template_error(self):
        """Jinja2Engine raises TemplateError in case of exception."""
        engine = Jinja2Engine()
        self.assertRaises(TemplateError,
                          engine.render,
                          u'{% if foo %}Unclosed IF',
                          {})
