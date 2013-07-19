# -*- coding: utf-8 -*-
"""Tools around webob requests."""
from webob.acceptparse import MIMENilAccept


def accepted_types(request):
    """Return list of accepted content types from request's 'accept' header."""
    if isinstance(request.accept, MIMENilAccept):  # Not explicitely requested.
        return ['*/*']  # Default.
    return [item for item in request.accept]
