# -*- coding: utf-8 -*-


class TemplateError(Exception):
    """A template failed to be rendered."""
    pass


class DataParsingError(Exception):
    """Input data failed to be parsed."""
