# -*- coding: utf-8 -*-
"""Tests around the functions to select templates."""
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from pyramid.httpexceptions import HTTPNotAcceptable

from diecutter.engines.django import DjangoEngine
from diecutter.engines.jinja import Jinja2Engine
from diecutter.service import Service
from diecutter.settings import DEFAULTS


class EngineSelectorTestCase(unittest.TestCase):
    """Tests around the functions to select templates."""
    def setUp(self):
        self.service = Service()

    def test_engine_factory(self):
        request = mock.Mock()
        request.registry = mock.Mock()
        request.registry.settings = DEFAULTS

        request.headers = {}
        self.assertEquals(self.service.get_engine_factory(request),
                          Jinja2Engine)

        request.headers = {"diecutter_template_engine": 'django'}
        self.assertEquals(self.service.get_engine_factory(request),
                          DjangoEngine)

        request.headers = {"diecutter_template_engine": "<invalid>"}
        self.assertRaises(HTTPNotAcceptable,
                          self.service.get_engine_factory, request)
