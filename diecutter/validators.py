# -*- coding: utf-8 -*-


def token_validator(request):
    default = u''
    reference_token = request.registry.settings.get('diecutter.token', default)
    request_token = request.POST.get('token', default)
    if request_token != reference_token:
        request.errors.add('authentication', 'token', 'invalid token')
        request.errors.status = 403
        return request.errors
