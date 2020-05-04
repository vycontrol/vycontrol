from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

import vyos



def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    static_list = vyos.get_static(hostname_default)

    template = loader.get_template('static/list.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
        'static_list' : static_list
    }   
    return HttpResponse(template.render(context, request))

