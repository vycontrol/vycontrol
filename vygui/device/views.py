from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos

def index(request):
    interfaces = vyos.get_interfaces()
    
    template = loader.get_template('device/index.html')
    context = {
        'interfaces': interfaces,
    }
    return HttpResponse(template.render(context, request))

def interface(request, interface_type, interface_name):
    interface = vyos.get_interface(interface_type, interface_name)
    
    template = loader.get_template('device/interface.html')
    context = { 
        'interface': interface,
    }   
    return HttpResponse(template.render(context, request))

