# -*- coding: utf-8 -*-
"""Jinja2 template engine."""
import os

from jinja2 import Environment
from jinja2.exceptions import UndefinedError, TemplateSyntaxError

from .base import Engine
from ..exceptions import TemplateError


def path_join(*args, **kwargs):
    """Return ``args`` joined as file paths like with os.path.join().

    >>> from diecutter.engines.jinja import path_join
    >>> path_join('foo', 'bar')
    'foo/bar'

    Paths are normalized.

    >>> path_join('foo', '..', 'bar')
    'bar'

    You can pass an extra keyword argument 'target_os': a value in os.name
    capabilities.

    >>> path_join('foo', 'bar', target_os='posix')
    'foo/bar'

    Currently, this is using os.path, i.e. the separator and rules for the
    computer running Jinja2 engine. A NotImplementedError exception will be
    raised if 'os' argument differs from 'os.name'.

    >>> import os
    >>> os.name == 'posix'  # Sorry if you are running tests on another OS.
    True
    >>> path_join('foo', 'bar', target_os='nt')  # Doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    NotImplementedError: Cannot join path with "nt" style. Host OS is "posix".

    """
    target_os = kwargs.get('target_os', None)
    if target_os and target_os is not os.name:
        raise NotImplementedError('Cannot join path with "{target}" style. '
                                  'Host OS is "{host}".'.format(
                                      target=target_os,
                                      host=os.name))
    result = os.path.join(*args)
    result = path_normalize(result, target_os)
    return result


def path_normalize(path, target_os=None):
    """Normalize path (like os.path.normpath) for given os.

    >>> from diecutter.engines.jinja import path_normalize
    >>> path_normalize('foo/bar')
    'foo/bar'
    >>> path_normalize('foo/toto/../bar')
    'foo/bar'

    Currently, this is using os.path, i.e. the separator and rules for the
    computer running Jinja2 engine. A NotImplementedError exception will be
    raised if 'os' argument differs from 'os.name'.

    >>> import os
    >>> os.name == 'posix'  # Sorry if you are running tests on another OS.
    True
    >>> path_normalize('foo/bar', target_os='nt')  # Doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    NotImplementedError: Cannot join path with "nt" style. Host OS is "posix".

    """
    if target_os and target_os is not os.name:
        raise NotImplementedError('Cannot join path with "{target}" style. '
                                  'Host OS is "{host}".'.format(
                                      target=target_os,
                                      host=os.name))
    return os.path.normpath(path)


class Jinja2Engine(Engine):
    """Jinja2 template engine."""
    def __init__(self, environment=None):
        if environment is None:
            environment = Environment()
        self.environment = environment
        self.register_environment_functions()

    def register_environment_functions(self):
        """Populate self.environment.globals with some global functions."""
        self.environment.globals['path_join'] = path_join
        self.environment.globals['path_normalize'] = path_normalize

    def render(self, template, context):
        """Return the rendered template against context."""
        try:
            template = self.environment.from_string(template)
        except TemplateSyntaxError as e:
            raise TemplateError(e)
        try:
            return template.render(**context)
        except (UndefinedError, TypeError) as e:
            raise TemplateError(e)
