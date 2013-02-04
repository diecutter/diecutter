# -*- coding: utf-8 -*-
"""Tests around diecutter.contextextractors."""
import unittest

from pyramid import testing

from diecutter import contextextractors


class PostTestCase(unittest.TestCase):
    """Test diecutter.contextextractors.extract_post_context."""
    def request_factory(self, post={}):
        """Return mock request instance."""
        class MockRequest(object):
            def __init__(self, post={}):
                self.POST = post
        return MockRequest(post)

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
