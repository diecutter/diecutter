# -*- coding: utf-8 -*-
"""Tests around diecutter.contextextractors."""
import unittest

from pyramid import testing

from diecutter import contextextractors


class PostTestCase(unittest.TestCase):
    """Test diecutter.contextextractors.extract_post_context."""
    def request_factory(self, data={}):
        """Return mock request instance."""
        class MockRequest(object):
            def __init__(self, data={}):
                self.POST = data
        return MockRequest(data)

    def test_data(self):
        """extract_post_request() returns request.post data."""
        # Empty data.
        request = self.request_factory()
        context = contextextractors.extract_post_context(request)
        self.assertEqual(context, {})
        # Not empty.
        request = self.request_factory({'dummy': 'hello world!'})
        context = contextextractors.extract_post_context(request)
        self.assertEqual(context, request.POST)

    def test_copy(self):
        """extract_post_request() returns copy of request's data."""
        request = self.request_factory({'dummy': 'hello world!'})
        context = contextextractors.extract_post_context(request)
        self.assertFalse(context is request.POST)
        del context['dummy']
        self.assertEqual(context, {})
        self.assertIn('dummy', request.POST)


class JsonTestCase(unittest.TestCase):
    """Test diecutter.contextextractors.extract_json_context."""
    def request_factory(self, data={}):
        """Return mock request instance."""
        class MockRequest(object):
            def __init__(self, data={}):
                self.json_body = data
        return MockRequest(data)

    def test_data(self):
        """extract_post_request() returns request.json_body data."""
        # Empty data.
        request = self.request_factory()
        context = contextextractors.extract_json_context(request)
        self.assertEqual(context, {})
        # Not empty.
        request = self.request_factory({'dummy': 'hello world!'})
        context = contextextractors.extract_json_context(request)
        self.assertEqual(context, request.json_body)

    def test_copy(self):
        """extract_post_request() returns copy of request's json_body."""
        request = self.request_factory({'dummy': 'hello world!'})
        context = contextextractors.extract_json_context(request)
        self.assertFalse(context is request.json_body)
        del context['dummy']
        self.assertEqual(context, {})
        self.assertIn('dummy', request.json_body)


class IniTestCase(unittest.TestCase):
    """Test diecutter.contextextractors.extract_ini_context."""
    def request_factory(self, data={}):
        """Return mock request instance."""
        class MockRequest(object):
            def __init__(self, ini=u''):
                self.body = ini
        return MockRequest(data)

    def test_empty(self):
        """extract_ini_context() with empty data returns empty context."""
        data = u''
        request = self.request_factory(data)
        context = contextextractors.extract_ini_context(request)
        self.assertEqual(context, {})

    def test_config_parser(self):
        """extract_ini_context() accepts standard ConfigParser input."""
        data = """[section1]
option1 = 1
option2 = 2

[section2]
optiona = A
optionb = B
"""
        request = self.request_factory(data)
        context = contextextractors.extract_ini_context(request)
        self.assertEqual(context, {'section1': {'option1': '1',
                                                'option2': '2'},
                                   'section2': {'optiona': 'A',
                                                'optionb': 'B'}})

    def test_globals(self):
        """extract_ini_context() accepts input with no sections."""
        data = """global1 = g1
global2 = g2

[section1]
option1 = o1
option2 = o2
"""
        request = self.request_factory(data)
        context = contextextractors.extract_ini_context(request)
        self.assertEqual(context, {'global1': 'g1',
                                   'global2': 'g2',
                                   'section1': {'option1': 'o1',
                                                'option2': 'o2'}})
