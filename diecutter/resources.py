# -*- coding: utf-8 -*-
"""Resources exposed on APIs."""
import os
from os.path import dirname, exists, isdir, isfile, join, relpath
import zipfile
from cStringIO import StringIO

from diecutter.jinja import Jinja2Engine
from diecutter.exceptions import TemplateError


def render_path(path, context):
    """Take a context and render the path.

    >>> from diecutter.resources import render_path
    >>> render_path('circus/circus_+watcher_name+.ini',
    ...             {'watcher_name': 'diecutter'})
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
        """Constructor.

        path
          An absolute path on the filesystem.

        engine
          A class that implements render(template, context).

        """
        self.path = path
        self.engine = engine

    @property
    def exists(self):
        return exists(self.path)

    @property
    def content_type(self):
        raise NotImplementedError()

    def read(self):
        """Return resource content."""
        raise NotImplementedError()

    def render(self, context):
        """Return resource rendered against context."""
        raise NotImplementedError()


class FileResource(Resource):
    @property
    def exists(self):
        return isfile(self.path)

    @property
    def content_type(self):
        return 'text/plain'

    def read(self):
        """Return the template source file."""
        return open(self.path, 'r').read().decode('utf-8')

    def render(self, context):
        """Return the template rendered against context."""
        try:
            return self.engine.render(self.read(), context)
        except TemplateError as e:
            print self.path
            raise TemplateError('%s: %s' % (self.path, e))


class DirResource(Resource):
    @property
    def exists(self):
        return isdir(self.path)

    @property
    def content_type(self):
        return 'application/zip'

    def read(self):
        """Return directory tree."""
        lines = []
        full_root = dirname(self.path)
        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs.sort()
            for file_name in sorted(files):
                lines.append(
                    join(relpath(root, full_root).lstrip('./'),
                         file_name))
        return '\n'.join(lines)

    def render(self, context):
        """Return archive of files in tree rendered against context."""
        full_root = dirname(self.path)
        temp_file = StringIO()
        temp_zip = zipfile.ZipFile(temp_file, 'w',
                                   compression=zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs.sort()
            for file_name in sorted(files):
                resource = Resource(join(root, file_name),
                                    self.engine)
                path = join(relpath(root, full_root).lstrip('./'),
                            file_name)
                try:
                    temp_zip.writestr(
                        render_path(path, context),
                        resource.render(context).encode('utf-8'))
                except (TemplateError, UnicodeDecodeError) as e:
                    raise TemplateError('%s: %s' % (path, e))
        temp_zip.close()

        return temp_file.getvalue()
