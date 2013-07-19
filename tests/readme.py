# -*- coding: utf-8 -*-
"""Tests around project's readme file."""
import os
from StringIO import StringIO
import sys
import unittest

import docutils.core
import docutils.io


tests_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(tests_dir)
build_dir = os.path.join(project_dir, 'var', 'docs', 'html')


class ReadMeTestCase(unittest.TestCase):
    """Test suite around README file."""
    def test_readme_build(self):
        """README builds to HTML without errors.

        This is required for PyPI to display a nice HTML page instead of plain
        text project description.

        """
        # Run build.
        source = open(os.path.join(project_dir, 'README')).read()
        writer_name = 'html'
        stderr_backup = sys.stderr
        sys.stderr = StringIO()
        output, pub = docutils.core.publish_programmatically(
            source=source,
            source_class=docutils.io.StringInput,
            source_path=None,
            destination_class=docutils.io.StringOutput,
            destination=None,
            destination_path=None,
            reader=None,
            reader_name='standalone',
            parser=None,
            parser_name='restructuredtext',
            writer=None,
            writer_name=writer_name,
            settings=None,
            settings_spec=None,
            settings_overrides=None,
            config_section=None,
            enable_exit_status=False)
        sys.stderr = stderr_backup
        errors = pub._stderr.stream.getvalue()
        # Check result.
        self.assertFalse(errors, "Docutils reported errors while building "
                                 "readme content from reStructuredText to "
                                 "HTML. So PyPI would display the readme as "
                                 "text instead of HTML. Errors are:\n%s"
                                 % errors)
