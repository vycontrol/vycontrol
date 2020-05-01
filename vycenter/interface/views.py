from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos

from config.models import Instance


def index(request):
    hostname_default = vyos.get_hostname_prefered(request)

    all_instances = vyos.instance_getall()

    interfaces = vyos.get_interfaces(hostname_default)
    
    template = loader.get_template('interface/index.html')
    context = {
        'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
    }
    return HttpResponse(template.render(context, request))

def interfaceshow(request, interface_type, interface_name):
    all_instances = vyos.instance_getall()

    hostname_default = vyos.get_hostname_prefered(request)
    
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    
    template = loader.get_template('interface/show.html')
    context = { 
        'interface': interface,
        'instances': all_instances,
        'interface_type' : interface_type,
        'interface_name' : interface_name,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))


def interfacefirewall(request, interface_type, interface_name):
    all_instances = vyos.instance_getall()

    hostname_default = vyos.get_hostname_prefered(request)
    
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    
    template = loader.get_template('interface/show.html')
    context = { 
        'interface': interface,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'interface_type' : interface_type,
        'interface_name' : interface_name,        
    }   
    return HttpResponse(template.render(context, request))


