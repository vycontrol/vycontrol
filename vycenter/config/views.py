from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import vyos


def index(request):
    #interfaces = vyos.get_interfaces()
    
    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
    }   
    return HttpResponse(template.render(context, request))



def instance(request):
    #interfaces = vyos.get_interfaces()
    
    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
    }   
    return HttpResponse(template.render(context, request))

def instance_add(request):
    #interfaces = vyos.get_interfaces()
    
    template = loader.get_template('config/instance_add.html')
    context = { 
        #'interfaces': interfaces,
    }   
    return HttpResponse(template.render(context, request))





