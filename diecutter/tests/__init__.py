# -*- coding: utf-8 -*-
"""Tests."""
import os

from webtest.http import StopableWSGIServer

import diecutter.wsgi


def demo_template_dir():
    """Return absolute path to diecutter's demo template dir."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(tests_dir)
    project_dir = os.path.dirname(package_dir)
    demo_dir = os.path.join(project_dir, 'demo')
    return os.path.normpath(os.path.join(demo_dir, 'templates'))


def demo_settings(**settings):
    defaults = {  # Defaults
        'template_engine': 'diecutter.engines.jinja:Jinja2Engine',
        'filename_template_engine': 'diecutter.engines.filename:FilenameEngine'
    }
    defaults.update(settings)
    return dict([('diecutter.{key}'.format(key=key), value)
                 for key, value in defaults.items()])


def webtest_server(application):
    """Return (running) WebTest's StopableWSGIServer for application."""
    server = StopableWSGIServer.create(application)
    server.wait()
    return server


def demo_server():
    """Return (running) WebTest's StopableWSGIServer for demo."""
    template_dir = demo_template_dir()
    settings = demo_settings(template_dir=template_dir)
    global_settings = {}
    application = diecutter.wsgi.for_paste(global_settings, **settings)
    return webtest_server(application)
