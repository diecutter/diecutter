# -*- coding: utf-8 -*-
"""Tests around diecutter.resources."""
from os import mkdir
from os.path import exists, isdir, isfile, join
import unittest

from diecutter import resources
from diecutter.exceptions import TemplateError
from diecutter.tests import temporary_directory


class MockEngine(object):
    """Template engine mock."""
    def __init__(self, render_result=u'this is a mock', fail=None):
        self.render_result = render_result
        self.fail = fail

    def render(self, *args, **kwargs):
        """Return tuple (:py:attr:`render_result`, ``args``, ``kwargs``)."""
        if self.fail:
            raise TemplateError(self.fail)
        return (self.render_result, args, kwargs)


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

    def test_read_empty(self):
        """FileResource.read() empty file returns empty string."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            resource = resources.FileResource(path=path, engine=None)
            self.assertEqual(resource.read(), u'')

    def test_read_utf8(self):
        """FileResource.read() decodes UTF-8 files."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            content = u'Thé ou café ?'
            open(path, 'w').write(content.encode('utf8'))
            resource = resources.FileResource(path=path, engine=None)
            self.assertEqual(resource.read(), content)

    def test_render(self):
        """FileResource.render() renders template against context."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            template = u'Tea or coffee'
            context = {'a': 1, 'b': 2}
            engine = MockEngine(u'this is render result')
            open(path, 'w').write(template.encode('utf8'))
            resource = resources.FileResource(path=path, engine=engine)
            result = resource.render(context)
            self.assertEqual(result, (u'this is render result',  # Mock result.
                                      (template, context),  # args.
                                      {}))  # kwargs.

    def test_render_error(self):
        """FileResource.render() raises ``TemplateError`` in case of fail."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            template = u'Tea or coffee'
            context = {'a': 1, 'b': 2}
            engine = MockEngine(fail=u'This is an error message')
            open(path, 'w').write(template.encode('utf8'))
            resource = resources.FileResource(path=path, engine=engine)
            self.assertRaises(TemplateError, resource.render, context)


class DirResourceTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.resources.DirResource`."""
    def test_content_type(self):
        """DirResource.content_type is 'application/zip'."""
        resource = resources.DirResource(path='', engine=None)
        self.assertEqual(resource.content_type, 'application/zip')

    def test_exists_false(self):
        """DirResource.exists is False if dir doesn't exist at path."""
        path = join('i', 'do', 'not', 'exist')
        self.assertFalse(exists(path))  # Just in case.
        resource = resources.DirResource(path=path, engine=None)
        self.assertTrue(resource.exists is False)

    def test_exists_dir(self):
        """DirResource.exists is True if path points a directory."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            mkdir(path)
            self.assertTrue(isdir(path))  # Check initial status.
            resource = resources.DirResource(path=path, engine=None)
            self.assertTrue(resource.exists is True)

    def test_exists_file(self):
        """DirResource.exists is False if path points a file."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            self.assertTrue(isfile(path))  # Check initial status.
            resource = resources.DirResource(path=path, engine=None)
            self.assertTrue(resource.exists is False)

    def test_read_empty(self):
        """DirResource.read() empty dir returns empty string."""
        with temporary_directory() as path:
            resource = resources.DirResource(path=path, engine=None)
            self.assertEqual(resource.read(), u'')

    def test_read_one_flat(self):
        """DirResource.read() one file returns one filename."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            file_path = join(dir_path, 'one')
            open(file_path, 'w')
            resource = resources.DirResource(path=dir_path, engine=None)
            self.assertEqual(resource.read(), 'dummy/one')

    def test_read_two_flat(self):
        """DirResource.read() two files returns two filenames."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            for filename in ('one', 'two'):
                file_path = join(dir_path, filename)
                open(file_path, 'w')
            resource = resources.DirResource(path=dir_path, engine=None)
            self.assertEqual(resource.read(), "dummy/one\ndummy/two")
