# -*- coding: utf-8 -*-
"""Tests around :py:mod:`diecutter.github`."""
import os
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import diecutter.github
from diecutter.utils import temporary_directory


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
