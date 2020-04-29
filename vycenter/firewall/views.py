from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect


import vyos



def index(request):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall_all = vyos.get_firewall_all(hostname_default)

    template = loader.get_template('firewall/list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all':  firewall_all
    }   
    return HttpResponse(template.render(context, request))



def show(request, name):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall_all = vyos.get_firewall_all(hostname_default)

    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all':  firewall_all
    }   
    return HttpResponse(template.render(context, request))


