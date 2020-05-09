from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.template.defaultfilters import register


import vyos
from perms import is_authenticated


from config.models import Instance

import pprint


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@is_authenticated    
def index(request):
       
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall()
    firewall_all = vyos.get_firewall_all(hostname_default)
    interfaces = vyos.get_interfaces(hostname_default)

    interface_firewall_in = {}
    interface_firewall_out = {}

    for interface_type in interfaces:
        for interface_name in interfaces[interface_type]:
            pprint.pprint(interface_name)
            try:
                interface_firewall_in[interface_name] = interfaces[interface_type][interface_name]['firewall']['in']['name']
            except:
                pass
            try:
                interface_firewall_out[interface_name] = interfaces[interface_type][interface_name]['firewall']['out']['name']
            except:
                pass

    fw_changed = False
    for el in request.POST:
        pprint.pprint(request.POST)
 
        if el.startswith('firewall-ipv4-in') and request.POST[el]:
            pos = el.split(".")
            
            interface_type = pos[1]
            interface_name = pos[2]
            firewall_name = request.POST[el]
            if firewall_name == "--remove--":
                result1 = vyos.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "in")         
            else:
                result1 = vyos.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "in", firewall_name)         

            pprint.pprint(result1)  
            fw_changed = True
        elif el.startswith('firewall-ipv4-out') and request.POST[el]:
            pos = el.split(".")
            
            interface_type = pos[1]
            interface_name = pos[2]
            firewall_name = request.POST[el]
            if firewall_name == "--remove--":
                result1 = vyos.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "out")
            else:
                result1 = vyos.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "out", firewall_name)
            pprint.pprint(result1)              
            fw_changed = True
            
    if fw_changed == True:
        return redirect('interface:interface-list')

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
        'interface_firewall_in' : interface_firewall_in,
        'interface_firewall_out' : interface_firewall_out,
        'username': request.user,        
    }
    return HttpResponse(template.render(context, request))

@is_authenticated    
def interfaceshow(request, interface_type, interface_name):
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    firewall_all = vyos.get_firewall_all(hostname_default)   
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    
    template = loader.get_template('interface/show.html')
    context = { 
        'interface': interface,
        'instances': all_instances,
        'interface_type' : interface_type,
        'interface_name' : interface_name,
        'hostname_default': hostname_default,
        'firewall_all' : firewall_all,
        'username': request.user,                       
    }   
    return HttpResponse(template.render(context, request))


@is_authenticated    
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
        'username': request.user,        
    }   
    return HttpResponse(template.render(context, request))


