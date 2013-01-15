""" Cornice services.
"""
import json
from datetime import datetime
from cornice import Service
from pyramid.exceptions import NotFound
from os import makedirs
from os.path import join, abspath, dirname, exists

from diecutter import __version__ as VERSION
from diecutter.exceptions import TemplateError
from diecutter.settings import TEMPLATE_DIR
from diecutter.utils import Resource
from diecutter.validators import token_validator


template_service = Service(name='template_service', path='/',
                           description="The template API")

conf_template = Service(name='template', path='/{template_path:.+}',
                        description="Return the template render or raw")


@template_service.get()
def get_hello(request):
    """Returns Hello in JSON."""
    return {'diecutter': 'Hello', 'version': VERSION}


@conf_template.put(validators=(token_validator,))
def put_template(request):
    filename = request.matchdict['template_path']
    input_file = request.POST['file'].file

    file_path = abspath(join(TEMPLATE_DIR, filename))
    if not file_path.startswith(TEMPLATE_DIR):
        NotFound('Ressource not found.')

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


@conf_template.get()
def get_conf_template(request):
    resource = Resource(request.matchdict['template_path'])
    if not resource.exists:
        return NotFound('Template not found')
    request.response.content_type = 'text/plain'
    request.response.write(resource.read())
    return request.response


@conf_template.post()
def post_conf_template(request):
    resource = Resource(request.matchdict['template_path'])
    try:
        context = json.loads(request.body)
    except:
        context = request.POST.copy()
    context['diecutter'] = {
        'api_url': '%s://%s' % (request.environ['wsgi.url_scheme'],
                                request.environ['HTTP_HOST']),
        'version': VERSION,
        'now': datetime.now()}
    if not resource.exists:
        return NotFound('Template not found')
    request.response.content_type = resource.content_type
    try:
        request.response.write(resource.render(context))
    except TemplateError as e:
        request.response.status_int = 500
        request.response.write(json.dumps(str(e)))
    return request.response
