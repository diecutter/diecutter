# -*- coding: utf-8 -*-
"""Utilities to run a test server."""
import os

from webtest.http import StopableWSGIServer

import diecutter.wsgi


def demo_template_dir():
    """Return absolute path to diecutter's demo template dir, as best guess.

    This function supports two situations:

    * you use it in code repository's root, i.e. ``demo/`` folder is in the
      same folder than ``diecutter/tests/__init__.py``.

    * `tox` runs the documentation build, i.e. ``demo/`` folder is in the
      code repository's root, whereas ``diecutter/tests/__init__.py`` lives in
      ``.tox/...``.

    """
    here = os.path.dirname(os.path.abspath(__file__))
    here_parts = here.split(os.path.sep)
    is_tox = '.tox' in here_parts
    if is_tox:
        tox_index = here_parts.index('.tox')
        project_dir = here
        for i in range(len(here_parts) - tox_index):
            project_dir = os.path.dirname(project_dir)
    else:
        project_dir = os.path.dirname(here)
    demo_dir = os.path.join(project_dir, 'demo')
    return os.path.normpath(os.path.join(demo_dir, 'templates'))


def demo_settings(**settings):
    defaults = {  # Defaults
        'engine': 'jinja2',
        'filename_engine': 'filename'
    }
    defaults.update(settings)
    return dict([('diecutter.{key}'.format(key=key), value)
                 for key, value in defaults.items()])


def webtest_server(application):
    """Return (running) WebTest's StopableWSGIServer for application."""
    server = StopableWSGIServer.create(application)
    server.wait()
    return server


def demo_server(template_dir=None):
    """Return (running) WebTest's StopableWSGIServer for demo."""
    if template_dir is None:
        template_dir = demo_template_dir()
    settings = demo_settings(template_dir=template_dir)
    global_settings = {}
    application = diecutter.wsgi.for_paste(global_settings, **settings)
    return webtest_server(application)
