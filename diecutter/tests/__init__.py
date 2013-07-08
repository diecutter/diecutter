# -*- coding: utf-8 -*-
"""Tests."""
import os

from webtest.http import StopableWSGIServer

import diecutter.service


def demo_template_dir():
    """Return absolute path to diecutter's demo template dir."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(tests_dir)
    project_dir = os.path.dirname(package_dir)
    demo_dir = os.path.join(project_dir, 'demo')
    return os.path.normpath(os.path.join(demo_dir, 'templates'))


def settings(template_dir):
    """Shortcut to get diecutter settings for use in WSGI application."""
    return {'diecutter.template_dir': template_dir}


def wsgi_application(settings={}):
    """Return diecutter WSGI application for tests.

    Uses WebTest.

    """
    global_config = {}
    application = diecutter.service.main(global_config, **settings)
    return application


def wsgi_server(application):
    """Return (running) WebTest's StopableWSGIServer for application."""
    server = StopableWSGIServer.create(application)
    server.wait()
    return server
