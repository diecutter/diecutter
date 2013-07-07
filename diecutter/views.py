"""Cornice services."""
from datetime import datetime
import logging
from os import makedirs
from os.path import join, abspath, dirname, exists, isdir, normpath

from cornice import Service
from pyramid.exceptions import ConfigurationError, Forbidden, NotFound
from pyramid.httpexceptions import HTTPNotImplemented, HTTPNotAcceptable
from webob.acceptparse import MIMENilAccept

from diecutter import __version__ as VERSION
from diecutter.engines.filename import FilenameEngine
from diecutter.engines.jinja import Jinja2Engine
from diecutter import resources
from diecutter.contextextractors import extract_context
from diecutter.validators import token_validator


logger = logging.getLogger(__name__)


template_service = Service(name='template_service', path='/',
                           description="The template API",
                           cors_origins=('*',))

conf_template = Service(name='template', path='/{template_path:.+}',
                        description="Return the template render or raw")


def get_template_dir(request):
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


def get_resource_path(request):
    """Return validated (absolute) resource path from request.

    Checks that resource path is inside request's template_dir.

    """
    template_dir = get_template_dir(request)
    filename = request.matchdict['template_path']
    file_path = normpath(abspath(join(template_dir, filename)))
    if not file_path.startswith(template_dir):
        NotFound('Ressource not found.')
    if filename.endswith('/'):  # Preserve trailing '/'
        file_path += '/'
    return file_path


def get_resource(request):
    """Return the resource matching request.

    Return value is a :py:class:`FileResource` or :py:class`DirResource`.

    """
    path = get_resource_path(request)
    engine = Jinja2Engine()
    filename_engine = FilenameEngine()
    if isdir(path):
        resource = resources.DirResource(path=path, engine=engine,
                                         filename_engine=filename_engine)
    else:
        resource = resources.FileResource(path=path, engine=engine,
                                          filename_engine=filename_engine)
    return resource


def to_boolean(value):
    _BOOL_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                    '0': False, 'no': False, 'false': False, 'off': False}

    value = str(value).lower().strip()
    if value not in _BOOL_STATES:
        raise ValueError(value)
    return _BOOL_STATES[value]


def is_readonly(request):
    """Return "readonly" flag status (boolean) for request.

    As an example, PUT operations should be forbidden if readonly flag is On.

    """
    return to_boolean(request.registry.settings.get('diecutter.readonly',
                                                    False))


def get_hello(request):
    """Returns Hello in JSON."""
    return {'diecutter': 'Hello', 'version': VERSION}


def put_template(request):
    if is_readonly(request):
        raise Forbidden('This diecutter server is readonly.')
    filename = request.matchdict['template_path']
    input_file = request.POST['file'].file

    file_path = get_resource_path(request)

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


def get_conf_template(request):
    resource = get_resource(request)
    if not resource.exists:
        return NotFound('Template not found')
    request.response.content_type = 'text/plain'
    request.response.write(resource.read())
    return request.response


def get_accepted_types(request):
    """Return list of accepted content types from request's 'accept' header."""
    if isinstance(request.accept, MIMENilAccept):  # Not explicitely requested.
        return ['*/*']  # Default.
    return [item for item in request.accept]


def get_writers(request, resource, context):
    """Return iterable of writers."""
    from diecutter.writers import (zip_directory_response, file_response,
                                   targz_directory_response)
    if resource.is_file:
        return [file_response]
    else:
        accepted_mime_types = get_accepted_types(request)
        # Reference.
        mime_type_map = {'application/zip': [zip_directory_response],
                         'application/gzip': [targz_directory_response],
                         }
        # Aliases.
        mime_type_map['application/x-gzip'] = mime_type_map['application/gzip']
        # Fallback.
        mime_type_map['*/*'] = mime_type_map['application/zip']
        for accepted_mime_type in accepted_mime_types:
            try:
                return mime_type_map[accepted_mime_type]
            except KeyError:
                pass
        raise HTTPNotAcceptable('Supported mime types: %s'
                                % ', '.join(sorted(mime_type_map.keys())))


def get_dispatcher(request, resource, context, writers):
    """Return simple dispatcher (later, would read configuration)."""
    return FirstResultDispatcher(writers)


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


def post_conf_template(request):
    resource = get_resource(request)
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
    writers = get_writers(request, resource, context)
    dispatcher = get_dispatcher(request, resource, context, writers)
    response = dispatcher(request, resource, context)
    return response


template_service.add_view('GET', get_hello)
conf_template.add_view('PUT', put_template, validators=(token_validator,))
conf_template.add_view('GET', get_conf_template)
conf_template.add_view('POST', post_conf_template)
