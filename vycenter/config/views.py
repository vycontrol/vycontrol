from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos

from .models import Instance


def index(request):
    #interfaces = vyos.get_interfaces()
    
    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
    }   
    return HttpResponse(template.render(context, request))



def instances(request):
    all_instances = Instance.objects.all()

    template = loader.get_template('config/instances.html')
    context = { 
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))

def instance_add(request):
    #interfaces = vyos.get_interfaces()
    
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
    }   
    return HttpResponse(template.render(context, request))





