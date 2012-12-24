# -*- coding: utf-8 -*-
import os
from os.path import join, exists, isfile, isdir, dirname, relpath
import zipfile
from cStringIO import StringIO

from diecutter.settings import TEMPLATE_DIR
from diecutter.jinja import Jinja2Engine


class Resource(object):
    def __init__(self, path, engine=Jinja2Engine()):
        self.path = join(TEMPLATE_DIR, path)
        self.engine = engine

    @property
    def exists(self):
        return exists(self.path)

    @property
    def is_file(self):
        return isfile(self.path)

    @property
    def is_dir(self):
        return isdir(self.path)

    @property
    def content_type(self):
        if self.is_file:
            return 'text/plain'
        else:
            return 'application/zip'

    def read(self):
        """Return the template source file."""
        if self.is_file:
            return open(self.path, 'r').read()
        elif self.is_dir:
            lines = []
            full_root = dirname(self.path)
            for root, dirs, files in os.walk(self.path):
                for file_name in sorted(files):
                    lines.append(
                        join(relpath(root, full_root).lstrip('./'),
                             file_name))
            return '\n'.join(lines)

    def render(self, context):
        """Return the template rendered against context."""
        if self.is_file:
            return self.engine.render(self.read(), context)
        elif self.is_dir:
            full_root = dirname(self.path)
            temp_file = StringIO()
            with zipfile.ZipFile(temp_file, 'w',
                                 compression=zipfile.ZIP_DEFLATED) as temp_zip:
                for root, dirs, files in os.walk(self.path):
                    for file_name in sorted(files):
                        resource = Resource(join(relpath(root, TEMPLATE_DIR),
                                                 file_name))
                        temp_zip.writestr(
                            join(relpath(root, full_root).lstrip('./'),
                                 file_name),
                            resource.render(context))
            return temp_file.getvalue()
