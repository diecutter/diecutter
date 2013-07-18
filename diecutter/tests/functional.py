# -*- coding: utf-8 -*-
"""Functional tests: run test server and make requests on it."""
import os
import unittest
import zipfile
import tarfile

from webtest import TestApp, Upload

import diecutter.wsgi
from diecutter.utils import temporary_directory


class FunctionalTestCase(unittest.TestCase):
    def setUp(self):
        """Run test server with temporary settings."""
        global_config = {}
        self.template_dir = temporary_directory()
        self.template_dir.__enter__()
        settings = {'diecutter.template_dir': self.template_dir.path}
        application = diecutter.wsgi.for_paste(global_config, **settings)
        self.app = TestApp(application)

    def tearDown(self):
        """Cleanup temporary template dir."""
        self.template_dir.__exit__()

    def test_version(self):
        """GET on root displays "hello" and version number as JSON."""
        response = self.app.get('/', status=200)
        self.assertEqual(response.body,
                         """{"diecutter": "Hello", "version": "%s"}"""
                         % diecutter.__version__)

    def test_get_file_404(self):
        """GET a file resource that doesn't exist returns HTTP 404."""
        # Setup.
        server_filename = os.path.join(self.template_dir.path, 'hello')
        self.assertFalse(os.path.exists(server_filename))  # Initial check.
        # Perform request.
        self.app.get('/hello', status=404)

    def test_get_file(self):
        """GET a file resource returns file contents."""
        # Setup.
        content = "Hello world!"
        server_filename = os.path.join(self.template_dir.path, 'hello')
        open(server_filename, 'w').write(content)
        # Perform request.
        response = self.app.get('/hello', status=200)
        # Check content.
        self.assertEqual(response.body, content)

    def test_get_directory(self):
        """GET a directory resource returns directory listing."""
        # Setup.
        dir_path = os.path.join(self.template_dir.path, 'dummy')
        os.mkdir(dir_path)
        for dir_name in ('a', 'b'):
            os.mkdir(os.path.join(dir_path, dir_name))
            for file_name in ('one', 'two'):
                file_path = os.path.join(dir_path, dir_name, file_name)
                open(file_path, 'w')
        # Perform request.
        response = self.app.get('/dummy/', status=200)
        # Check content.
        self.assertEqual(response.body,
                         '\n'.join(['a/one', 'a/two', 'b/one', 'b/two']))

    def test_put_file(self):
        """PUT a file as attachment writes file in templates directory."""
        # Initial state.
        server_filename = os.path.join(self.template_dir.path, 'hello')
        self.assertFalse(os.path.isfile(server_filename))
        # Setup.
        url = '/hello'
        client_filename = "fake.txt"
        content = "Hello {{ who }}"
        files = Upload(client_filename, content)
        # Perform request.
        response = self.app.put(url, {'file': files}, status=201)
        # Check response.
        self.assertEqual(response.body, """{"diecutter": "Ok"}""")
        # Check that the file is present server-side.
        self.assertTrue(os.path.isfile(server_filename))
        self.assertEqual(open(server_filename).read(), content)

    def test_put_file_subdirs(self):
        """PUT a file in subdirectories creates those directories."""
        # Initial state.
        first_dir = os.path.join(self.template_dir.path, 'some')
        second_dir = os.path.join(first_dir, 'thing')
        server_filename = os.path.join(second_dir, 'hello')
        self.assertFalse(os.path.exists(first_dir))
        self.assertFalse(os.path.exists(second_dir))
        self.assertFalse(os.path.exists(server_filename))
        # Setup.
        url = '/some/thing/hello'
        client_filename = "fake.txt"
        content = "Hello {{ who }}"
        files = Upload(client_filename, content)
        # Perform request.
        response = self.app.put(url, {'file': files}, status=201)
        # Check response.
        self.assertEqual(response.body, """{"diecutter": "Ok"}""")
        # Check that the file is present server-side.
        self.assertTrue(os.path.isfile(server_filename))
        self.assertEqual(open(server_filename).read(), content)

    def test_post_file(self):
        """POST context for template returns rendered content."""
        # Setup.
        content = "Hello {{ who }}!"
        server_filename = os.path.join(self.template_dir.path, 'hello')
        open(server_filename, 'w').write(content)
        # Perform request.
        response = self.app.post('/hello', {'who': 'world'}, status=200)
        # Check content.
        self.assertEqual(response.body, "Hello world!")

    def test_post_directory_targz(self):
        """POST context for directory returns TAR.GZ file content."""
        # Setup.
        dir_path = os.path.join(self.template_dir.path, 'dummy')
        os.mkdir(dir_path)
        for dir_name in ('a', 'b'):
            os.mkdir(os.path.join(dir_path, dir_name))
            for file_name in ('one', 'two'):
                file_path = os.path.join(dir_path, dir_name, file_name)
                content = "Content of %s/%s: {{ foo }}" % (dir_name, file_name)
                open(file_path, 'w').write(content)
        # Perform request.
        response = self.app.post('/dummy/', {'foo': 'bar'}, status=200)
        # Check content.
        filename = os.path.join(self.template_dir.path, 'response.zip')
        open(filename, 'w').write(response.body)
        self.assertTrue(tarfile.is_tarfile(filename))
        try:
            archive = tarfile.open(filename, mode='r:gz')
            self.assertEqual(archive.getnames(),
                             ['a/one', 'a/two', 'b/one', 'b/two'])
            self.assertEqual(archive.extractfile('a/one').read(),
                             'Content of a/one: bar')
        finally:
            archive.close()

    def test_post_directory_zip(self):
        """POST context for directory with accept header returns ZIP file."""
        # Setup.
        dir_path = os.path.join(self.template_dir.path, 'dummy')
        os.mkdir(dir_path)
        for dir_name in ('a', 'b'):
            os.mkdir(os.path.join(dir_path, dir_name))
            for file_name in ('one', 'two'):
                file_path = os.path.join(dir_path, dir_name, file_name)
                content = "Content of %s/%s: {{ foo }}" % (dir_name, file_name)
                open(file_path, 'w').write(content)
        # Perform request.
        response = self.app.post('/dummy/', {'foo': 'bar'},
                                 headers={'accept': 'application/zip'},
                                 status=200)
        # Check content.
        zip_filename = os.path.join(self.template_dir.path, 'response.zip')
        open(zip_filename, 'w').write(response.body)
        self.assertTrue(zipfile.is_zipfile(zip_filename))
        try:
            zip_file = zipfile.ZipFile(zip_filename)
            self.assertEqual(zip_file.namelist(),
                             ['a/one', 'a/two', 'b/one', 'b/two'])
            self.assertEqual(zip_file.read('a/one'), 'Content of a/one: bar')
            self.assertTrue(zip_file.testzip() is None)
        finally:
            zip_file.close()
