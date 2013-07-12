# -*- coding: utf-8 -*-
"""Tests around :py:mod:`diecutter.github`."""
import os
from StringIO import StringIO
import tarfile
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pyramid.exceptions
import requests

import diecutter.github
from diecutter.utils import chdir, execute, temporary_directory


class GithubLoaderTestCase(unittest.TestCase):
    """Tests around :py:class:`diecutter.github.GithubLoader`."""
    def test_github_clone(self):
        """github_clone clones repository in a directory."""
        with temporary_directory() as output_dir:
            loader = diecutter.github.GithubLoader(output_dir)
            current_dir = os.path.abspath(os.path.dirname(__file__))
            diecutter_dev_repo = os.path.dirname(os.path.dirname(current_dir))
            url_mock = mock.Mock(return_value=diecutter_dev_repo)
            loader.github_clone_url = url_mock
            loader.github_clone('fake-user', 'fake-project')
            url_mock.assert_called_once_with('fake-user', 'fake-project')
            self.assertTrue(os.path.isdir(os.path.join(output_dir, '.git')))

    def test_github_clone_error(self):
        """github_clone raises NotFound on error."""
        with temporary_directory() as output_dir:
            loader = diecutter.github.GithubLoader(output_dir)
            execute_mock = mock.Mock(return_value=(1, '', 'error'))
            with mock.patch('diecutter.github.execute', new=execute_mock):
                with self.assertRaises(pyramid.exceptions.NotFound):
                    loader.github_clone('fake-user', 'fake-project')

    def test_github_checkout(self):
        """github_checkout clones and checkouts repository at revision."""
        with temporary_directory() as output_dir:
            loader = diecutter.github.GithubLoader(output_dir)
            current_dir = os.path.abspath(os.path.dirname(__file__))
            diecutter_dev_repo = os.path.dirname(os.path.dirname(current_dir))
            url_mock = mock.Mock(return_value=diecutter_dev_repo)
            loader.github_clone_url = url_mock
            clone_mock = mock.Mock(wraps=loader.github_clone)
            loader.github_clone = clone_mock
            loader.github_checkout('fake-user', 'fake-project',
                                   'efdf0c4a1c97d01a709ec308a0b509073c7264f6')
            clone_mock.assert_called_once_with('fake-user', 'fake-project')
            self.assertTrue(os.path.isdir(os.path.join(output_dir, '.git')))
            with chdir(output_dir):
                code, stdout, stderr = execute(['git', 'log', '-n 1',
                                                '--pretty=oneline'])
            self.assertEqual(code, 0)
            self.assertEqual(stdout,
                             'efdf0c4a1c97d01a709ec308a0b509073c7264f6 First draft\n')

    def test_github_checkout_error(self):
        """github_checkout raises NotFound on error."""
        with temporary_directory() as output_dir:
            loader = diecutter.github.GithubLoader(output_dir)
            current_dir = os.path.abspath(os.path.dirname(__file__))
            diecutter_dev_repo = os.path.dirname(os.path.dirname(current_dir))
            url_mock = mock.Mock(return_value=diecutter_dev_repo)
            loader.github_clone_url = url_mock
            with self.assertRaises(pyramid.exceptions.NotFound):
                loader.github_checkout('fake-user', 'fake-project',
                                       'this-revision-does-not-exist')

    def setup_targz(self, path, project, commit):
        """Create archive file in ``path``."""
        with tarfile.open(path, mode='w:gz') as archive:
            greetings_content = 'Hello {name}!'
            greetings_file = StringIO(greetings_content)
            greetings_name = '{project}-{commit}/greetings.txt'.format(
                project=project, commit=commit)
            greetings_info = tarfile.TarInfo(name=greetings_name)
            greetings_info.size = len(greetings_content)
            greetings_info.type = tarfile.REGTYPE
            archive.addfile(greetings_info, fileobj=greetings_file)

    def test_github_targz(self):
        """github_targz downloads and extracts archive in directory."""
        with temporary_directory() as github_mock_dir:
            archive_name = os.path.join(github_mock_dir, 'foo.tar.gz')
            self.setup_targz(archive_name, 'diecutter', 'master')
            with open(archive_name, 'r') as archive:
                content_mock = mock.Mock(return_value=archive)
                with temporary_directory() as output_dir:
                    loader = diecutter.github.GithubLoader(output_dir)
                    loader.github_targz_content = content_mock
                    loader.github_targz('fake-user', 'diecutter', 'master')
                    self.assertTrue(
                        os.path.exists(os.path.join(output_dir,
                                                    'diecutter-master',
                                                    'greetings.txt')))

    def test_github_targz_content(self):
        """github_targz_content downloads and returns archive stream."""
        with temporary_directory() as github_mock_dir:
            archive_name = os.path.join(github_mock_dir, 'foo.tar.gz')
            self.setup_targz(archive_name, 'diecutter', 'master')
            with open(archive_name, 'r') as archive:
                response_mock = mock.MagicMock()
                response_mock.raw = archive
                response_mock.status_code = 200
                get_mock = mock.Mock(return_value=response_mock)
                with mock.patch('diecutter.github.requests.get', new=get_mock):
                    with temporary_directory() as output_dir:
                        loader = diecutter.github.GithubLoader(output_dir)
                        content = loader.github_targz_content('fake-url')
                        self.assertTrue(archive is content)

    def test_github_targz_error(self):
        """github_targz_content raises requests exceptions."""
        with temporary_directory() as github_mock_dir:
            archive_name = os.path.join(github_mock_dir, 'foo.tar.gz')
            self.setup_targz(archive_name, 'diecutter', 'master')
            get_mock = mock.Mock(
                side_effect=requests.exceptions.ConnectionError)
            with mock.patch('diecutter.github.requests.get', new=get_mock):
                with temporary_directory() as output_dir:
                    loader = diecutter.github.GithubLoader(output_dir)
                    self.assertRaises(
                        requests.exceptions.ConnectionError,
                        loader.github_targz_content,
                        'fake-url')

    def test_github_targz_content_not_found(self):
        """github_targz_content raises NotFound if Github returns 404."""
        with temporary_directory() as github_mock_dir:
            archive_name = os.path.join(github_mock_dir, 'foo.tar.gz')
            self.setup_targz(archive_name, 'diecutter', 'master')
            response_mock = mock.MagicMock()
            response_mock.status_code = 404
            get_mock = mock.Mock(return_value=response_mock)
            with mock.patch('diecutter.github.requests.get', new=get_mock):
                with temporary_directory() as output_dir:
                    loader = diecutter.github.GithubLoader(output_dir)
                    self.assertRaises(
                        pyramid.exceptions.NotFound,
                        loader.github_targz_content,
                        'fake-url')
