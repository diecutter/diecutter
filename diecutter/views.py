""" Cornice services.
"""
import json
from os.path import abspath, join, dirname, exists, basename
from cornice import Service
from pyramid.exceptions import NotFound
from jinja2 import Template

TEMPLATE_DIR = join(dirname(abspath(__file__)), 'templates')


def get_template(template_name):
    """Return the template string from a template_name."""
    template = join(TEMPLATE_DIR, basename(template_name))
    if exists(template):
        return open(template).read()


class Jinja2Engine(object):
    def render(self, template, context):
        """Return the rendered template against context."""
        template = Template(template)
        return template.render(**context)

engine = Jinja2Engine()

template_service = Service(name='template_service', path='/',
                           description="The template API")

conf_template = Service(name='template', path='/{template_name}',
              description="Return the template render or raw")


@template_service.get()
def get_hello(request):
    """Returns Hello in JSON."""
    return {'diecutter': 'Hello'}


@conf_template.put()
def put_template(request):
    filename = request.matchdict['template_name']
    input_file = request.POST['file'].file

    file_path = join(TEMPLATE_DIR, filename)
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
    template = get_template(request.matchdict['template_name'])
    if template:
        request.response.content_type = "text/plain"
        request.response.write(template)
        return request.response
    return NotFound('Template not found')


@conf_template.post()
def post_conf_template(request):
    template = get_template(request.matchdict['template_name'])
    try:
        context = json.loads(request.body)
    except:
        context = request.POST.copy()
    if template:
        request.response.content_type = "text/plain"
        request.response.write(engine.render(template, context))
        return request.response
    return NotFound('Template not found')
