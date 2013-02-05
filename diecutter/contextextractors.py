# -*- coding: utf-8 -*-
"""Utilities to extract context dictionary from request."""


def extract_post_context(request):
    """Extract and return context from a standard POST request."""
    return request.POST.copy()


def extract_json_context(request):
    """Extract and return context from a application/json request."""
    return request.json_body.copy()


def extract_ini_context(request):
    """Extract and return context from a text/ini (ConfigParser) request."""
    from ConfigParser import ConfigParser
    from cStringIO import StringIO
    context = {}
    parser = ConfigParser()
    parser.readfp(StringIO('[__globals__]\n' + request.body))
    for option, value in parser.items('__globals__'):
        context[option] = value
    parser.remove_section('__globals__')
    for section in parser.sections():
        context[section] = {}
        for option, value in parser.items(section):
            context[section][option] = value
    return context


CONTEXT_EXTRACTORS = {
    '': extract_post_context,  # Default fallback.
    'application/x-www-form-urlencoded': extract_post_context,
    'application/json': extract_json_context,
    'text/plain': extract_ini_context,
}
"""Default context extractors configuration.

This configuration is used as fallback value if EXTRACTORS_SETTINGS is not in
Pyramid's registry.

This is a dictionary where:

* keys are (lowercase) content-types.
* values are callables which accept one ``request`` argument and return a
  dictionary (or dictionary-like object).

"""

EXTRACTORS_SETTING = 'diecutter.context_extractors'
"""Key in Pyramid registry where context extractors configuration lives."""


def get_context_extractors(request):
    """Return context extractors configuration from request."""
    try:
        return request.registry.settings[EXTRACTORS_SETTING]
    except KeyError:
        return CONTEXT_EXTRACTORS


def extract_context(request):
    """Extract context dictionary from request and return it.

    Raise :py:class:`NotImplementedError` if request input (content-type) is
    not supported.

    """
    context_extractors = get_context_extractors(request)
    try:
        extractor = context_extractors[request.content_type]
    except KeyError:
        raise NotImplementedError('Unsupported input content-type %s'
                                  % request.content_type)
    return extractor(request)
