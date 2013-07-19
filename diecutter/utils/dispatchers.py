# -*- coding: utf-8 -*-
"""Execution control."""


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
