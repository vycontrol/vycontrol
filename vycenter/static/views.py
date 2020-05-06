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
    #static_list = vyos.get_route_static(hostname_default)
    static_list = None
    
    template = loader.get_template('static/list.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
        'static_list' : static_list
    }   
    return HttpResponse(template.render(context, request))



def static(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    static_list = vyos.get_route_static(hostname_default)

    error_message = None
    if 'subnet' in request.POST and 'nexthop' in request.POST:
        #return1 = vyos.set_route_static(hostname_default, request.POST['subnet'], request.POST['nexthop'])
        return1 = False
        if return1 == False: 
            error_message = 'Cannot add static route.'
        else:
           return redirect('static:static-list')


    template = loader.get_template('static/static.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
        'static_list' : static_list,
        'error_message' : error_message,
    }   
    return HttpResponse(template.render(context, request))

