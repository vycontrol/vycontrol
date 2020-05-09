import functools

from django.shortcuts import redirect
from django.urls import reverse

from config.models import Instance

import vyos

def is_authenticated(func):
    @functools.wraps(func)
    def wrapper_perm(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
           return redirect('%s?next=%s' % (reverse('registration-login'), request.path))

        hostname_default = vyos.get_hostname_prefered(request)


        value = func(*args, **kwargs)
        return value
    return wrapper_perm