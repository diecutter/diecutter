# -*- coding: utf-8 -*-
from diecutter.settings import TOKEN


def token_validator(request):
    if TOKEN != request.POST.get('token', ''):
        request.errors.add('authentication', 'token', 'invalid token')
        request.errors.status = 403
        return request.errors
