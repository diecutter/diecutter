# -*- coding: utf-8 -*-
"""Resources exposed on APIs."""
import os
from os.path import basename, isdir, isfile, join, relpath
import zipfile
from cStringIO import StringIO

from diecutter.exceptions import TemplateError


class Resource(object):
    def __init__(self, path='', engine=None, filename_engine=None):
        """Constructor.

        path
          An absolute path on the filesystem.

        engine
          A class that implements render(template, context).
          This one is used to render file contents.

        filename_engine
          A class that implements render(template, context).
          This one is used to render filenames.

        """
        self.path = path
        self.engine = engine
        self.filename_engine = filename_engine

    @property
    def exists(self):
        raise NotImplementedError()

    @property
    def content_type(self):
        raise NotImplementedError()

    def read(self):
        """Return resource content."""
        raise NotImplementedError()

    def render(self, context):
        """Return resource rendered against context."""
        raise NotImplementedError()

    def render_filename(self, path, context):
        """Return rendered filename against context using FilenameEngine."""
        return self.filename_engine.render(path, context)


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
    """Container for other files and directories resources."""
    @property
    def exists(self):
        return isdir(self.path)

    @property
    def content_type(self):
        return 'application/zip'

    def relative_filename(self, filename):
        """Return filename relative to :py:attr:`path`.

        >>> from diecutter.resources import DirResource
        >>> resource = DirResource(path='abs/path/no-trailing')
        >>> resource.relative_filename('abs/path/no-trailing/name')
        'no-trailing/name'
        >>> resource.relative_filename('abs/path/no-trailing/nested/name')
        'no-trailing/nested/name'

        Trailing slash in :py:attr:`path` affects returned value.

        >>> resource = DirResource(path='abs/path/trailing/')
        >>> resource.relative_filename('abs/path/trailing/name')
        'name'
        >>> resource.relative_filename('abs/path/trailing/nested/name')
        'nested/name'

        """
        prefix = basename(self.path)
        return join(prefix, relpath(filename, self.path))

    def read_tree(self):
        """Generate list of paths to contained resources."""
        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs.sort()
            for file_name in sorted(files):
                yield join(root, file_name)

    def read(self):
        """Return directory tree as a list of paths of file resources."""
        lines = [self.relative_filename(line) for line in self.read_tree()]
        return '\n'.join(lines)

    def render_tree(self, context):
        """Generate list of (resource_path, filename, context).

        Included resources may depend on context, i.e. some resources may be
        used several times, or skipped.

        Rendered filenames may depend on context, i.e. variables may be used
        to render filenames.

        Context may change for each resource.

        """
        for resource_path in self.read_tree():
            filename = self.relative_filename(resource_path)
            filename = self.render_filename(filename, context)
            yield (resource_path, filename, context)

    def render(self, context):
        """Return archive of files in tree rendered against context."""
        temp_file = StringIO()
        temp_zip = zipfile.ZipFile(temp_file, 'w',
                                   compression=zipfile.ZIP_DEFLATED)
        for resource_path, filename, context in self.render_tree(context):
            resource = FileResource(join(self.path, resource_path),
                                    self.engine)
            try:
                content = resource.render(context).encode('utf-8')
            except (TemplateError, UnicodeDecodeError) as e:
                raise TemplateError('%s: %s' % (resource_path, e))
            temp_zip.writestr(filename, content)
        temp_zip.close()
        return temp_file.getvalue()
