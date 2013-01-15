# -*- coding: utf-8 -*-
import os
from os.path import join, exists, isfile, isdir, dirname, relpath
import zipfile
from cStringIO import StringIO

from diecutter.settings import TEMPLATE_DIR
from diecutter.jinja import Jinja2Engine
from diecutter.exceptions import TemplateError


def render_path(path, context):
    """Take a context and render the path.
    >>> from diecutter.utils import render_path
    >>> render_path('circus/circus_+watcher_name+.ini',
    ...     dict(watcher_name='diecutter'))
    'circus/circus_diecutter.ini'

    """
    for key, val in context.iteritems():
        try:
            path = path.replace('+%s+' % key, val)
        except TypeError:
            pass
    return path


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
            return open(self.path, 'r').read().decode('utf-8')
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
                        path = join(relpath(root, full_root).lstrip('./'),
                                    file_name)
                        try:
                            temp_zip.writestr(
                                render_path(path, context),
                                resource.render(context).encode('utf-8'))
                        except TemplateError as e:
                            raise TemplateError('%s: %s' % (path, e))
                        except UnicodeDecodeError as e:
                            raise TemplateError('%s: %s' % (path, e))

            return temp_file.getvalue()
