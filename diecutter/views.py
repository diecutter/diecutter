"""Cornice services."""
from datetime import datetime
import logging
from os import makedirs
from os.path import join, abspath, dirname, exists, isdir, normpath

from pyramid.exceptions import ConfigurationError, Forbidden, NotFound
from pyramid.httpexceptions import HTTPNotImplemented, HTTPNotAcceptable
from webob.acceptparse import MIMENilAccept

from diecutter import __version__ as VERSION
from diecutter import resources
from diecutter.contextextractors import extract_context
from diecutter.validators import token_validator


logger = logging.getLogger(__name__)


class Service(object):
    """Base class for diecutter services."""
    def hello(self, request):
        """Returns Hello and API version in JSON."""
        return {'diecutter': 'Hello', 'version': VERSION}

    def get(self, request):
        raise NotImplementedError()

    def post(self, request):
        raise NotImplementedError()

    def put(self, request):
        raise NotImplementedError()

    def get_resource(self, request):
        """Return the resource object (instance) matching request."""
        raise NotImplementedError()

    def get_engine(self, request):
        """Return configured template engine to render templates."""
        from diecutter.engines.jinja import Jinja2Engine
        return Jinja2Engine()

    def get_filename_engine(self, request):
        """Return configured template engine to render filenames.

        This is not used for dynamic trees.

        """
        from diecutter.engines.filename import FilenameEngine
        return FilenameEngine()

    def get_writers(self, request, resource, context):
        """Return iterable of writers."""
        from diecutter.writers import (zip_directory_response, file_response,
                                       targz_directory_response)
        if resource.is_file:
            return [file_response]
        else:
            accepted_mime_types = get_accepted_types(request)
            # Reference.
            mime_map = {'application/zip': [zip_directory_response],
                        'application/gzip': [targz_directory_response],
                        }
            # Aliases.
            mime_map['application/x-gzip'] = mime_map['application/gzip']
            # Fallback.
            mime_map['*/*'] = mime_map['application/zip']
            for accepted_mime_type in accepted_mime_types:
                try:
                    return mime_map[accepted_mime_type]
                except KeyError:
                    pass
            raise HTTPNotAcceptable('Supported mime types: %s'
                                    % ', '.join(sorted(mime_map.keys())))

    def get_dispatcher(self, request, resource, context, writers):
        """Return simple dispatcher (later, would read configuration)."""
        return FirstResultDispatcher(writers)

    def is_readonly(self, request):
        """Return "readonly" flag status (boolean) for request.

        As an example, PUT operations should be forbidden if readonly flag is
        On.

        """
        return to_boolean(request.registry.settings.get('diecutter.readonly',
                                                        False))


class LocalService(Service):
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


def to_boolean(value):
    _BOOL_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                    '0': False, 'no': False, 'false': False, 'off': False}

    value = str(value).lower().strip()
    if value not in _BOOL_STATES:
        raise ValueError(value)
    return _BOOL_STATES[value]


def get_accepted_types(request):
    """Return list of accepted content types from request's 'accept' header."""
    if isinstance(request.accept, MIMENilAccept):  # Not explicitely requested.
        return ['*/*']  # Default.
    return [item for item in request.accept]


class FirstResultDispatcher(object):
    """A dispatcher that return the first result got from callables."""
    def __init__(self, runners=[]):
        self.runners = runners

    def __call__(self, *fargs, **kwargs):
        for runner in self.runners:
            result = runner(*fargs, **kwargs)
            if result is not None:
                return result
        return result


def register_service(config, name, service, path):
    """Register a diecutter service in Pyramid routing."""
    import cornice
    hello = cornice.Service(name='{name}_hello'.format(name=name),
                            path=path,
                            description="The template API",
                            cors_origins=('*',))
    template = cornice.Service(
        name='{name}_template'.format(name=name),
        path='%s{template_path:.+}' % path,
        description="Return the template render or raw")
    hello.add_view('GET', service.hello)
    template.add_view('PUT', service.put, validators=(token_validator,))
    template.add_view('GET', service.get)
    template.add_view('POST', service.post)
    cornice.register_service_views(config, hello)
    cornice.register_service_views(config, template)
