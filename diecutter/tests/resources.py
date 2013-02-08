# -*- coding: utf-8 -*-
"""Tests around diecutter.resources."""
from os import mkdir
from os.path import exists, isdir, isfile, join
import unittest

from diecutter import resources
from diecutter.tests import temporary_directory


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
        path = join('i', 'do', 'not', 'exist')
        self.assertFalse(exists(path))  # Just in case.
        resource = resources.FileResource(path=path, engine=None)
        self.assertTrue(resource.exists is False)

    def test_exists_dir(self):
        """FileResource.exists is False if path points a directory."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            mkdir(path)
            self.assertTrue(isdir(path))  # Check initial status.
            resource = resources.FileResource(path=path, engine=None)
            self.assertTrue(resource.exists is False)

    def test_exists_file(self):
        """FileResource.exists is True if path points a file."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            self.assertTrue(isfile(path))  # Check initial status.
            resource = resources.FileResource(path=path, engine=None)
            self.assertTrue(resource.exists is True)
