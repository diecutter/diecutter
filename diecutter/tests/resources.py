# -*- coding: utf-8 -*-
"""Tests around diecutter.resources."""
import json
from os import mkdir, sep
from os.path import exists, isdir, isfile, join
import unittest
try:
    from unittest import mock
except:
    import mock
import zipfile

from diecutter import resources
from diecutter.engines.mock import MockEngine
from diecutter.exceptions import TemplateError
from diecutter.tests import temporary_directory


class ResourceTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.resources.Resource`."""
    def test_init(self):
        """Resource constructor accepts optional ``path`` and ``engine``."""
        resource = resources.Resource()
        self.assertEqual(resource.path, '')
        self.assertEqual(resource.engine, None)
        resource = resources.Resource('path', 'engine')
        self.assertEqual(resource.path, 'path')
        self.assertEqual(resource.engine, 'engine')
        resource = resources.Resource(engine='engine', path='path')
        self.assertEqual(resource.path, 'path')
        self.assertEqual(resource.engine, 'engine')

    def test_exists(self):
        """Resource.exists property must be overriden by subclasses."""
        resource = resources.Resource()
        self.assertRaises(NotImplementedError, lambda: resource.exists)

    def test_content_type(self):
        """Resource.content_type property must be overriden by subclasses."""
        resource = resources.Resource()
        self.assertRaises(NotImplementedError, lambda: resource.content_type)

    def test_read(self):
        """Resource.read() must be overriden by subclasses."""
        resource = resources.Resource()
        self.assertRaises(NotImplementedError, resource.read)

    def test_render(self):
        """Resource.render() must be overriden by subclasses."""
        resource = resources.Resource()
        context = {}
        self.assertRaises(NotImplementedError, resource.render, context)

    def test_render_filename(self):
        """Resource.render_filename() renders filename against context."""
        # Initialize.
        input_filename = 'dummy.txt'
        context = {'some': 'data'}
        expected_output_filename = 'this is rendered filename'
        engine = MockEngine(expected_output_filename)
        resource = resources.Resource(filename_engine=engine)
        # Render.
        output_filename = resource.render_filename(input_filename, context)
        # Check.
        self.assertEqual(output_filename, expected_output_filename)
        self.assertEqual(engine.args, (input_filename, context))
        self.assertEqual(engine.kwargs, {})


class FileResourceTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.resources.FileResource`."""
    def test_content_type(self):
        """FileResource.content_type is 'text/plain'."""
        resource = resources.FileResource()
        self.assertEqual(resource.content_type, 'text/plain')

    def test_exists_false(self):
        """FileResource.exists is False if file doesn't exist at path."""
        path = join('i', 'do', 'not', 'exist')
        self.assertFalse(exists(path))  # Just in case.
        resource = resources.FileResource(path=path)
        self.assertTrue(resource.exists is False)

    def test_exists_dir(self):
        """FileResource.exists is False if path points a directory."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            mkdir(path)
            self.assertTrue(isdir(path))  # Check initial status.
            resource = resources.FileResource(path=path)
            self.assertTrue(resource.exists is False)

    def test_exists_file(self):
        """FileResource.exists is True if path points a file."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            self.assertTrue(isfile(path))  # Check initial status.
            resource = resources.FileResource(path=path)
            self.assertTrue(resource.exists is True)

    def test_read_empty(self):
        """FileResource.read() empty file returns empty string."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            resource = resources.FileResource(path=path)
            self.assertEqual(resource.read(), u'')

    def test_read_utf8(self):
        """FileResource.read() decodes UTF-8 files."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            content = u'Thé ou café ?'
            open(path, 'w').write(content.encode('utf8'))
            resource = resources.FileResource(path=path)
            self.assertEqual(resource.read(), content)

    def test_render(self):
        """FileResource.render() generates rendered template against context.

        It returns an iteratable or generator.

        """
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            template = u'Tea or coffee'
            context = {'a': 1, 'b': 2}
            engine = MockEngine(u'this is render result')
            open(path, 'w').write(template.encode('utf8'))
            resource = resources.FileResource(path=path, engine=engine)
            result = resource.render(context)
            result = ''.join(result)
            self.assertEqual(result, u'this is render result')
            self.assertEqual(engine.args, (template, context))
            self.assertEqual(engine.kwargs, {})

    def test_render_error(self):
        """FileResource.render() raises ``TemplateError`` in case of fail."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            template = u'Tea or coffee'
            context = {'a': 1, 'b': 2}
            engine = MockEngine(fail=TemplateError('This is an error message'))
            open(path, 'w').write(template.encode('utf8'))
            resource = resources.FileResource(path=path, engine=engine)
            self.assertRaises(TemplateError, resource.render, context)


class DirResourceTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.resources.DirResource`."""
    def test_content_type(self):
        """DirResource.content_type is 'application/zip'."""
        resource = resources.DirResource()
        self.assertEqual(resource.content_type, 'application/zip')

    def test_exists_false(self):
        """DirResource.exists is False if dir doesn't exist at path."""
        path = join('i', 'do', 'not', 'exist')
        self.assertFalse(exists(path))  # Just in case.
        resource = resources.DirResource(path=path)
        self.assertTrue(resource.exists is False)

    def test_exists_dir(self):
        """DirResource.exists is True if path points a directory."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            mkdir(path)
            self.assertTrue(isdir(path))  # Check initial status.
            resource = resources.DirResource(path=path)
            self.assertTrue(resource.exists is True)

    def test_exists_file(self):
        """DirResource.exists is False if path points a file."""
        with temporary_directory() as template_dir:
            path = join(template_dir, 'dummy')
            open(path, 'w')
            self.assertTrue(isfile(path))  # Check initial status.
            resource = resources.DirResource(path=path)
            self.assertTrue(resource.exists is False)

    def test_read_empty(self):
        """DirResource.read() empty dir returns empty string."""
        with temporary_directory() as path:
            resource = resources.DirResource(path=path)
            self.assertEqual(resource.read(), u'')

    def test_read_one_flat(self):
        """DirResource.read() one file returns one filename."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            file_path = join(dir_path, 'one')
            open(file_path, 'w')
            dir_path += sep
            resource = resources.DirResource(path=dir_path)
            self.assertEqual(resource.read(), 'one')

    def test_read_two_flat(self):
        """DirResource.read() two files returns two filenames."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            for file_name in ('one', 'two'):
                file_path = join(dir_path, file_name)
                open(file_path, 'w')
            dir_path += sep
            resource = resources.DirResource(path=dir_path)
            self.assertEqual(resource.read(), "one\ntwo")

    def test_read_nested(self):
        """DirResource.read() recurses nested files and directories."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            for dir_name in ('a', 'b'):
                mkdir(join(dir_path, dir_name))
                for file_name in ('one', 'two'):
                    file_path = join(dir_path, dir_name, file_name)
                    open(file_path, 'w')
            dir_path += sep
            resource = resources.DirResource(path=dir_path)
            self.assertEqual(resource.read(),
                             "a/one\na/two\nb/one\nb/two")

    def test_no_trailing_slash(self):
        """DirResource with no trailing slash uses dirname as prefix."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            file_path = join(dir_path, 'one')
            open(file_path, 'w')
            resource = resources.DirResource(path=dir_path)
            self.assertEqual(resource.read(), 'dummy/one')

    def test_trailing_slash(self):
        """DirResource with trailing slash uses dirname as prefix."""
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            file_path = join(dir_path, 'one')
            open(file_path, 'w')
            dir_path += sep
            resource = resources.DirResource(path=dir_path)
            self.assertEqual(resource.read(), 'one')

    def test_render_tree(self):
        """DirResource.render_tree() recurses nested files and directories."""
        expected_output_filename = 'rendered/{args[0]!s}'
        filename_engine = MockEngine(expected_output_filename)
        context = {'fake': 'fake-context'}
        with temporary_directory() as template_dir:
            dir_path = join(template_dir, 'dummy')
            mkdir(dir_path)
            for dir_name in ('+a+', 'b'):
                mkdir(join(dir_path, dir_name))
                for file_name in ('+one+', 'two'):
                    file_path = join(dir_path, dir_name, file_name)
                    open(file_path, 'w')
            dir_path += sep
            resource = resources.DirResource(path=dir_path,
                                             filename_engine=filename_engine)
            rendered = list(resource.render_tree(context))
            self.assertEqual(rendered,
                             [(join(template_dir, 'dummy', '+a+', '+one+'),
                               'rendered/+a+/+one+',
                               context),
                              (join(template_dir, 'dummy', '+a+', 'two'),
                               'rendered/+a+/two',
                               context),
                              (join(template_dir, 'dummy', 'b', '+one+'),
                               'rendered/b/+one+',
                               context),
                              (join(template_dir, 'dummy', 'b', 'two'),
                               'rendered/b/two',
                               context)])

    def test_has_tree_template(self):
        """DirResource.has_tree_template() checks if .diecutter-tree exists."""
        with temporary_directory() as template_dir:
            dir_path = template_dir
            resource = resources.DirResource(path=dir_path)
            self.assertFalse(resource.has_tree_template())
            open(join(dir_path, '.diecutter-tree'), 'w')
            self.assertTrue(resource.has_tree_template())

    def test_render_dynamic_tree(self):
        """DirResource.render_tree() uses .diecutter-tree template."""
        content_engine = mock.MagicMock()
        content_engine.render = lambda t, c: t
        filename_engine = mock.MagicMock()
        context = {'fake': 'fake-context'}
        with temporary_directory() as template_dir:
            dir_path = template_dir
            directory_tree = [{'template': 'template_one.txt',
                               'filename': '1.txt',
                               'context': {}},
                              {'template': 'template_two.txt',
                               'filename': '2.txt',
                               'context': {}}]
            open(join(dir_path, '.diecutter-tree'), 'w').write(
                json.dumps(directory_tree))
            dir_path += sep
            resource = resources.DirResource(path=dir_path,
                                             engine=content_engine,
                                             filename_engine=filename_engine)
            rendered = list(resource.render_tree(context))
            self.assertEqual(rendered,
                             [(unicode(join(template_dir, 'template_one.txt')),
                               u'1.txt',
                               context),
                              (unicode(join(template_dir, 'template_two.txt')),
                               u'2.txt',
                               context)])
        self.assertFalse(filename_engine.called)

    def test_render_dynamic_tree_relative_paths(self):
        """Raises exception if .diecutter-tree contains some non relative path.

        .. warning::

           This is a security test!

           Since dynamic tree templates can be defined by user, we have to
           check templates path. We don't want users to be able to render
           arbitrary locations on the filesystem.

        """
        content_engine = mock.MagicMock()
        content_engine.render = lambda t, c: t
        filename_engine = mock.MagicMock()
        context = {'fake': 'fake-context'}
        with temporary_directory() as template_dir:
            dir_path = template_dir
            directory_tree = [{'template': '../template_one.txt',
                               'filename': '1.txt',
                               'context': {}}]
            open(join(dir_path, '.diecutter-tree'), 'w').write(
                json.dumps(directory_tree))
            dir_path += sep
            resource = resources.DirResource(path=dir_path,
                                             engine=content_engine,
                                             filename_engine=filename_engine)
            generate_content = lambda: [(filename, ''.join(content))
                                        for (filename, content)
                                        in resource.render(context)]
            self.assertRaises(ValueError, generate_content)
        self.assertFalse(filename_engine.called)

    def test_render(self):
        """DirResource.render() returns an iterable of rendered templates."""
        with temporary_directory() as template_dir:
            # Setup.
            expected_filename = 'rendered-filename/{args[0]!s}'
            filename_engine = MockEngine(expected_filename)
            expected_content = u'rendered-content/{args[0]!s}'
            content_engine = MockEngine(expected_content)
            context = {'fake': 'fake-context'}
            dir_path = join(template_dir, 'dir')
            mkdir(dir_path)
            dir_path += sep
            file_path = join(dir_path, 'file')
            open(file_path, 'w').write('data')
            resource = resources.DirResource(path=dir_path,
                                             engine=content_engine,
                                             filename_engine=filename_engine)
            # Render.
            rendered = resource.render(context)
            # Check result.
            rendered = [part for part in rendered]
            self.assertEqual(len(rendered), 1)  # One file rendered.
            self.assertEqual(len(rendered[0]), 2)  # filename, content.
            self.assertEqual(rendered[0][0], 'rendered-filename/file')

            self.assertEqual(u''.join(rendered[0][1]),
                             u'rendered-content/data')

    def test_render_template_error(self):
        with temporary_directory() as template_dir:
            # Setup.
            expected_filename = 'rendered-filename/{args[0]!s}'
            filename_engine = MockEngine(expected_filename)
            content_engine = MockEngine(fail=TemplateError('error!'))
            context = {'fake': 'fake-context'}
            dir_path = join(template_dir, 'dir')
            mkdir(dir_path)
            dir_path += sep
            file_path = join(dir_path, 'file')
            open(file_path, 'w').write('data')
            resource = resources.DirResource(path=dir_path,
                                             engine=content_engine,
                                             filename_engine=filename_engine)
            # Render.
            generate_content = lambda: [(filename, ''.join(content))
                                        for (filename, content)
                                        in resource.render(context)]
            self.assertRaises(TemplateError, generate_content)
