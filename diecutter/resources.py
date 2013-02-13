# -*- coding: utf-8 -*-
"""Resources exposed on APIs."""
import os
from os.path import basename, isdir, isfile, join, relpath
import zipfile
from cStringIO import StringIO

from diecutter.exceptions import TemplateError


class Resource(object):
    def __init__(self, path='', engine=None):
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

    def read_tree(self):
        """Generate list of relative paths to contained resources."""
        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs.sort()
            prefix = relpath(root, self.path).lstrip('./')
            for file_name in sorted(files):
                yield join(prefix, file_name)

    def read(self):
        """Return directory tree as a list of paths of file resources."""
        prefix = basename(self.path)
        lines = [join(prefix, path) for path in self.read_tree()]
        return '\n'.join(lines)

    def render_filename(self, path, context):
        """Return rendered filename against context.

        .. warning::

           Only flat string variables are accepted. Other variables are ignored
           silently!

        """
        for key, val in context.iteritems():
            try:
                path = path.replace('+%s+' % key, val)
            except TypeError:
                pass
        return path

    def render_tree(self, context):
        """Generate list of (resource_path, filename, context).

        Included resources may depend on context, i.e. some resources may be
        used several times, or skipped.

        Rendered filenames may depend on context, i.e. variables may be used
        to render filenames.

        Context may change for each resource.

        """
        filename_prefix = basename(self.path)
        for resource_path in self.read_tree():
            filename = self.render_filename(resource_path, context)
            filename = join(filename_prefix, filename)
            yield (resource_path, filename, context)

    def render(self, context):
        """Return archive of files in tree rendered against context."""
        temp_file = StringIO()
        temp_zip = zipfile.ZipFile(temp_file, 'w',
                                   compression=zipfile.ZIP_DEFLATED)
        for resource_path, filename, context in self.render_tree:
            resource = FileResource(join(self.path, resource_path),
                                    self.engine)
            try:
                content = resource.render(context).encode('utf-8')
            except (TemplateError, UnicodeDecodeError) as e:
                raise TemplateError('%s: %s' % (resource_path, e))
            temp_zip.writestr(filename, content)
        temp_zip.close()
        return temp_file.getvalue()
