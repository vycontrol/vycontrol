from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect


import vyos



def index(request):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    template = loader.get_template('static/list.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))

