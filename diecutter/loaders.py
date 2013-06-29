import jinja2
import requests


class HttpLoader(jinja2.BaseLoader):
    """Load templates over HTTP.

    >>> from jinja2 import Environment
    >>> from diecutter.loaders import HttpLoader
    >>> http_loader = HttpLoader(u'https://raw.github.com/novagile/diecutter/master/demo/templates')
    >>> env = Environment(loader=http_loader)
    >>> template = env.get_template('greetings.txt')
    >>> print template.render(name='world')
    Hello world!
    >>> template = env.get_template('https://raw.github.com/novagile/diecutter/master/demo/templates/greetings.txt')
    >>> print template.render(name='world')
    Hello world!

    """
    def __init__(self, root=u''):
        self.root = root

    def get_url(self, environment, template):
        if template.startswith(u'http'):
            url = template
        else:
            url = '%s/%s' % (self.root, template)
        return url

    def get_source(self, environment, template):
        url = self.get_url(environment, template)
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise e
        if response.status_code == 404:
            raise jinja2.TemplateNotFound(template)
        source = response.text
        return source, url, lambda: False
