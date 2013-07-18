# -*- coding: utf-8 -*-
"""Service implementation for local files."""
from datetime import datetime
import logging
from os import makedirs
from os.path import join, abspath, dirname, exists, isdir, normpath

from pyramid.exceptions import ConfigurationError, Forbidden, NotFound
from pyramid.httpexceptions import HTTPNotImplemented

from diecutter import __version__ as VERSION
from diecutter import resources
from diecutter.contextextractors import extract_context
import diecutter.service


logger = logging.getLogger(__name__)


class LocalService(diecutter.service.Service):
    """A service that loads templates on local filesystem."""
    def get(self, request):
        resource = self.get_resource(request)
        if not resource.exists:
            return NotFound('Template not found')
        request.response.content_type = 'text/plain'
        request.response.write(resource.read())
        return request.response

    def post(self, request):
        resource = self.get_resource(request)
        try:
            context = extract_context(request)
        except NotImplementedError as e:
            raise HTTPNotImplemented(e.message)
        context['diecutter'] = {
            'api_url': '%s://%s' % (request.environ['wsgi.url_scheme'],
                                    request.environ['HTTP_HOST']),
            'version': VERSION,
            'now': datetime.now()}
        if not resource.exists:
            return NotFound('Template not found')
        writers = self.get_writers(request, resource, context)
        dispatcher = self.get_dispatcher(request, resource, context, writers)
        response = dispatcher(request, resource, context)
        return response

    def put(self, request):
        if self.is_readonly(request):
            raise Forbidden('This diecutter server is readonly.')
        filename = request.matchdict['template_path']
        input_file = request.POST['file'].file

        file_path = self.get_resource_path(request)

        if not exists(dirname(file_path)):
            makedirs(dirname(file_path))

        with open(file_path, 'w') as output_file:
            # Finally write the data to the output file
            input_file.seek(0)
            for line in input_file.readlines():
                output_file.write(line)
        request.response.status_int = 201
        request.response.headers['location'] = str('/%s' % filename)
        return {'diecutter': 'Ok'}

    def get_resource(self, request):
        """Return the resource matching request.

        Return value is a :py:class:`FileResource` or :py:class`DirResource`.

        """
        path = self.get_resource_path(request)
        engine = self.get_engine(request)
        filename_engine = self.get_filename_engine(request)
        if isdir(path):
            resource = resources.DirResource(path=path, engine=engine,
                                             filename_engine=filename_engine)
        else:
            resource = resources.FileResource(path=path, engine=engine,
                                              filename_engine=filename_engine)
        return resource

    def get_resource_path(self, request):
        """Return validated (absolute) resource path from request.

        Checks that resource path is inside request's template_dir.

        """
        template_dir = self.get_template_dir(request)
        filename = request.matchdict['template_path']
        file_path = normpath(abspath(join(template_dir, filename)))
        if not file_path.startswith(template_dir):
            NotFound('Ressource not found.')
        if filename.endswith('/'):  # Preserve trailing '/'
            file_path += '/'
        return file_path

    def get_template_dir(self, request):
        """Return validated template directory configuration for request."""
        try:
            template_dir = request.registry.settings['diecutter.template_dir']
        except KeyError:
            error_msg = 'Missing mandatory "diecutter.template_dir" setting.'
            raise ConfigurationError(error_msg)
        if not template_dir:
            error_msg = 'Mandatory "diecutter.template_dir" setting is empty.'
            raise ConfigurationError(error_msg)
        return template_dir
