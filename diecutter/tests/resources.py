# -*- coding: utf-8 -*-
"""Tests around diecutter.resources."""
from os.path import exists, isdir, isfile, join
import unittest

from diecutter import resources


class MockEngine(object):
    """Template engine mock."""
    def __init__(self, render_result=u'this is a mock'):
        self.render_result = render_result

    def render(self, template, context):
        """Return :py:attr:`render_result`."""
        return self.render_result


class FileResourceTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.resources.FileResource`."""
    def test_content_type(self):
        """FileResource.content_type is 'text/plain'."""
        resource = resources.FileResource(path='', engine=None)
        self.assertEqual(resource.content_type, 'text/plain')

    def test_exists_false(self):
        """FileResource.exists is False if file doesn't exist at path."""
        self.assertFalse
        path = join('i', 'do', 'not', 'exist')
        self.assertFalse(exists(path))  # Just in case.
        resource = resources.FileResource(path=path, engine=None)
        self.assertFalse(resource.exists)
