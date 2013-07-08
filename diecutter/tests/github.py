# -*- coding: utf-8 -*-
"""Tests around :py:mod:`diecutter.github`."""
import os
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pyramid.exceptions

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
        """github_checkout clones and checkouts repository at revision."""
        with temporary_directory() as output_dir:
            loader = diecutter.github.GithubLoader(output_dir)
            current_dir = os.path.abspath(os.path.dirname(__file__))
            diecutter_dev_repo = os.path.dirname(os.path.dirname(current_dir))
            url_mock = mock.Mock(return_value=diecutter_dev_repo)
            loader.github_clone_url = url_mock
            clone_mock = mock.Mock(wraps=loader.github_clone)
            loader.github_clone = clone_mock
            with self.assertRaises(pyramid.exceptions.NotFound):
                loader.github_checkout('fake-user', 'fake-project',
                                       'this-revision-does-not-exist')

    def test_github_targz(self):
        """github_targz downloads and extracts archive in directory."""
