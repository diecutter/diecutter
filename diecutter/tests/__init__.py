# -*- coding: utf-8 -*-
"""Tests."""
import os
import shutil
import tempfile

from webtest.http import StopableWSGIServer

import diecutter


class temporary_directory(object):
    """Create, yield, and finally delete a temporary directory.

    >>> from diecutter.tests import temporary_directory
    >>> with temporary_directory() as directory:
    ...     os.path.isdir(directory)
    True
    >>> os.path.exists(directory)
    False

    Deletion of temporary directory is recursive.

    >>> with temporary_directory() as directory:
    ...     filename = os.path.join(directory, 'sample.txt')
    ...     __ = open(filename, 'w').close()
    ...     os.path.isfile(filename)
    True
    >>> os.path.isfile(filename)
    False

    """
    def __enter__(self):
        """Create temporary directory and return its path."""
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Remove temporary directory recursively."""
        shutil.rmtree(self.path)


def demo_template_dir():
    """Return absolute path to diecutter's demo template dir."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(tests_dir)
    project_dir = os.path.dirname(package_dir)
    demo_dir = os.path.join(project_dir, 'demo')
    return os.path.normpath(os.path.join(demo_dir, 'templates'))


def settings(template_dir):
    """Shortcut to get diecutter settings for use in WSGI application."""
    return {
        'diecutter.template_dir': template_dir,
        'diecutter.template_engine': 'diecutter.engines.jinja:Jinja2Engine',
        'diecutter.filename_template_engine': 'diecutter.engines.filename:FilenameEngine'
    }


def wsgi_application(settings={}):
    """Return diecutter WSGI application for tests.

    Uses WebTest.

    """
    global_config = {}
    application = diecutter.main(global_config, **settings)
    #application = TestApp(application)
    return application


def wsgi_server(application):
    """Return (running) WebTest's StopableWSGIServer for application."""
    server = StopableWSGIServer.create(application)
    server.wait()
    return server
