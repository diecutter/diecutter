# -*- coding: utf-8 -*-
"""Tests around diecutter.engines."""
import unittest

from diecutter.engines.filename import FilenameEngine


class FilenameTestCase(unittest.TestCase):
    """Test :py:class:`diecutter.engines.filename.FilenameEngine`."""
    def test_render(self):
        """FilenameEngine.render() renders filename against context."""
        engine = FilenameEngine()
        rendered = engine.render('circus/circus_+watcher_name+.ini',
                                 {'watcher_name': 'diecutter'})
        self.assertEqual(rendered, 'circus/circus_diecutter.ini')

    def test_render_error(self):
        """FilenameEngine.render() only accepts flat string variables.

        .. warning::

           Only flat string variables are accepted. Other variables are ignored
           silently!

        """
        engine = FilenameEngine()
        # Nested variable.
        rendered = engine.render('+watcher.name+.ini',
                                 {'watcher': {'name': 'diecutter'}})
        self.assertEqual(rendered, '+watcher.name+.ini')
        # Non-string variable.
        rendered = engine.render('+name+.ini', {'name': 42})
        self.assertEqual(rendered, '+name+.ini')
