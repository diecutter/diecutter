# -*- coding: utf-8 -*-
"""Mock template engine, for use in tests."""
from diecutter.engines import Engine
from diecutter.exceptions import TemplateError


#: Default value used as :py:attr:`MockEngine.render_result`
default_render_result = u'RENDER WITH ARGS={args!s} AND KWARGS={kwargs!s}'


class MockEngine(Engine):
    """Template engine mock.

    Typical usage:

    >>> from diecutter.engines.mock import MockEngine
    >>> mock_result = u'this is expected result'
    >>> mock = MockEngine(mock_result)
    >>> args = ('arg 1', 'arg 2')
    >>> kwargs = {'kwarg1': 'kwarg 1', 'kwarg2': 'kwarg 2'}
    >>> mock.render(*args, **kwargs) == mock_result
    True
    >>> mock.args == args
    True
    >>> mock.kwargs == kwargs
    True

    You can use ``{args}`` and ``{kwargs}`` in mock result, because render()
    uses str.format().
    This feature is used by default:

    >>> mock = MockEngine()
    >>> mock.render_result
    u'RENDER WITH ARGS={args!s} AND KWARGS={kwargs!s}'
    >>> mock.render()
    u'RENDER WITH ARGS=() AND KWARGS={}'

    """
    def __init__(self, render_result=default_render_result, fail=None):
        #: Value to be returned by :py:meth:`render`.
        self.render_result = render_result

        #: Whether to raise a :py:class:`TemplateError` or not.
        #: Also, value used as message in the exception.
        self.fail = fail

        #: Stores positional arguments of the last call to :py:meth:`render`.
        self.args = None

        #: Stores keyword arguments of the last call to :py:meth:`render`.
        self.kwargs = None

    def render(self, *args, **kwargs):
        """Return self.render_result + populates args and kwargs.

        If self.fail is not None, then raises a TemplateError(self.fail).

        """
        if self.fail is not None:
            raise TemplateError(self.fail)
        self.args = args
        self.kwargs = kwargs
        return self.render_result.format(args=args, kwargs=kwargs)
