from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos

from .models import Instance


def index(request):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()

    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))



def instances(request):
    all_instances = vyos.instance_getall()
    

    template = loader.get_template('config/instances.html')
    context = { 
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))

def instance_add(request):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()

    if len(request.POST) > 0:
        instance = Instance()
        instance.alias = request.POST['alias']
        instance.hostname = request.POST['hostname']
        instance.port = request.POST['port']
        instance.key = request.POST['key']
        if 'https' in request.POST:
            instance.https = request.POST['https']
        else:
            instance.https = False
        instance_id = instance.save()
    else:
        instance_id = 0

    template = loader.get_template('config/instance_add.html')
    context = { 
        'instance_id': instance_id,
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))

def instance_conntry(request, hostname):
    all_instances = vyos.instance_getall()

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    connected = vyos.conntry(hostname)

    template = loader.get_template('config/instance_conntry.html')
    context = { 
        'instance': instance,
        "connected": connected,
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))



