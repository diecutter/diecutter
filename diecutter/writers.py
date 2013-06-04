# -*- coding: utf-8 -*-
"""Writers: utilities that write template output as response, files..."""
import json
import logging
import zipfile
from cStringIO import StringIO

from diecutter.exceptions import TemplateError


logger = logging.getLogger(__name__)


def file_response(request, resource, context):
    """Render file resource against context and return response."""
    request.response.content_type = 'text/plain'
    try:
        file_generator = resource.render(context)
        file_content = ''.join(file_generator)
    except TemplateError as e:
        request.response.status_int = 500
        logger.error('TemplateError caught: {error}'.format(error=e))
        request.response.write(json.dumps(str(e)))
    request.response.write(file_content)
    return request.response


def zip_directory(directory_generator):
    """Return a zip file built from generator ``template_output``."""
    temp_file = StringIO()
    temp_zip = zipfile.ZipFile(temp_file, 'w',
                               compression=zipfile.ZIP_DEFLATED)
    for filename, file_generator in directory_generator:
        content = ''.join(file_generator)
        temp_zip.writestr(filename, content)
    temp_zip.close()
    return temp_file.getvalue()


def zip_directory_response(request, resource, context):
    request.response.content_type = 'application/zip'
    try:
        directory_generator = resource.render(context)
        zip_content = zip_directory(directory_generator)
    except TemplateError as e:
        request.response.status_int = 500
        logger.error('TemplateError caught: {error}'.format(error=e))
        request.response.write(json.dumps(str(e)))
    request.response.write(zip_content)
    return request.response
