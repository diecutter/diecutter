"""Template engine specialized to render filenames."""
from diecutter.engines.base import Engine


class FilenameEngine(Engine):
    """"""
    def render(self, template, context):
        """Return rendered filename template against context.

        .. warning::

           Only flat string variables are accepted. Other variables are ignored
           silently!

        """
        for key, val in context.iteritems():
            try:
                template = template.replace('+%s+' % key, val)
            except TypeError:
                pass
        return template
