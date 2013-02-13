# -*- coding: utf-8 -*-
"""Template engines."""


class Engine(object):
    """Base class for template engines.

    Mostly used to document engine API.

    """
    def render(self, template, context):
        """Return the rendered template against context."""
        raise NotImplementedError()
