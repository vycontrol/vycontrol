from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos

from config.models import Instance

import pprint

def index(request):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall()
    firewall_all = vyos.get_firewall_all(hostname_default)
    interfaces = vyos.get_interfaces(hostname_default)

    for el in request.POST:
        if el.startswith('firewall-ipv4-in') and request.POST[el]:
            pos = el.split(".")
            
            interface_type = pos[1]
            interface_name = pos[2]
            firewall_name = request.POST[el]
            pprint.pprint(request.POST)

            result1 = vyos.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "in", firewall_name)
            print(result1)


    """
   if 'name' in request.POST:
        
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)

        if 'description' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "description", request.POST['description']]}
            result2 = vyos.set_config(hostname_default, cmd)
            print(result2)

        if 'action' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "default-action", request.POST['action']]}
            result3 = vyos.set_config(hostname_default, cmd)
            print(result3)

        return redirect('firewall:firewall-list')
    """


    template = loader.get_template('interface/index.html')
    context = {
        'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all' : firewall_all,
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


