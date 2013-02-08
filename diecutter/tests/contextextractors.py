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
        self.assertTrue('dummy' in request.POST)


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
        self.assertTrue('dummy' in request.json_body)


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


class GetContextExtractorsTestCase(unittest.TestCase):
    """Test contextextractors.get_context_extractors()."""
    def request_factory(self, settings={}):
        """Return mock request instance."""
        request = testing.DummyRequest()
        request.registry.settings = settings
        return request

    def test_default_configuration(self):
        """get_context_extractors() with no settings returns default ones."""
        request = self.request_factory(settings={})
        extractors = contextextractors.get_context_extractors(request)
        self.assertEqual(extractors, contextextractors.CONTEXT_EXTRACTORS)

    def test_custom_configuration(self):
        """get_context_extractors() reads request.registry.settings."""
        settings = {contextextractors.EXTRACTORS_SETTING: '123456'}
        request = self.request_factory(settings)
        extractors = contextextractors.get_context_extractors(request)
        self.assertEqual(extractors, '123456')


class ExtractContextTestCase(unittest.TestCase):
    """Test diecutter.contextextractors.extract_context()."""
    def extractor_factory(self, output):
        """Return callable that takes a request and returns output."""
        def extractor(request):
            return output
        return extractor

    def request_factory(self, extractors={}, content_type=''):
        """Return request with extractors setting and content_type."""
        request = testing.DummyRequest()
        request.content_type = content_type
        settings = {contextextractors.EXTRACTORS_SETTING: extractors}
        request.registry.settings = settings
        return request

    def test_no_mapping(self):
        """extract_context() raises exception if content-type isn't supported.

        """
        extractors = {}
        content_type = 'application/dummy'
        request = self.request_factory(extractors, content_type)
        self.assertRaises(NotImplementedError,
                          contextextractors.extract_context,
                          request)

    def test_mapping(self):
        """extract_context() uses extractor matching content-type."""
        output = {'a': 'AAA'}
        content_type = 'application/dummy'
        extractors = {content_type: self.extractor_factory(output)}
        request = self.request_factory(extractors, content_type)
        context = contextextractors.extract_context(request)
        self.assertEqual(context, output)
