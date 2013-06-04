# -*- coding: utf-8 -*-
"""Writers: utilities that write template output as response, files..."""
import json
import logging
from cStringIO import StringIO
import tarfile
import tempfile
import zipfile

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


def targz_directory(directory_generator):
    """Return a zip file built from generator ``template_output``."""
    with tempfile.TemporaryFile() as temporary_file:
        with tarfile.open(mode='w|gz', fileobj=temporary_file) as archive:
            for filename, file_generator in directory_generator:
                content = ''.join(file_generator)
                content_file = StringIO(content)
                content_file.seek(0)
                info = tarfile.TarInfo(name=filename)
                info.size = len(content)
                archive.addfile(tarinfo=info, fileobj=content_file)
        temporary_file.seek(0)
        return temporary_file.read()


def targz_directory_response(request, resource, context):
    request.response.content_type = 'application/gzip'
    try:
        directory_generator = resource.render(context)
        content = targz_directory(directory_generator)
    except TemplateError as e:
        request.response.status_int = 500
        logger.error('TemplateError caught: {error}'.format(error=e))
        request.response.write(json.dumps(str(e)))
    request.response.write(content)
    return request.response
