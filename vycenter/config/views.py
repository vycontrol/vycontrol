from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings


import pprint
import vyos

from .models import Instance

from django.contrib.auth.models import User



def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)


    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))


def users_list(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    users = User.objects.all()


    template = loader.get_template('config/users_list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'users' : users
    }   
    return HttpResponse(template.render(context, request))




def instances(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    print(all_instances)

    if hostname_default == None:
        if all_instances.count() > 0:
            for i in all_instances:
                pprint.pprint(i.hostname)
                instance_default(request, i.hostname)
            
        else:
            return redirect('config:instance-add')

    template = loader.get_template('config/instances.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,

    }   
    return HttpResponse(template.render(context, request))

def instance_add(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

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
        return redirect('config:instances')
    else:
        instance_id = 0

    template = loader.get_template('config/instance_add.html')
    context = { 
        'hostname_default': hostname_default,
        'instance_id': instance_id,
        'instances': all_instances,
    }   
    return HttpResponse(template.render(context, request))

def instance_conntry(request, hostname):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    connected = vyos.conntry(hostname)
    if connected == True:
        request.session['hostname'] = hostname


    template = loader.get_template('config/instance_conntry.html')
    context = { 
        'instance': instance,
        "connected": connected,
        'instances': all_instances,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))


def instance_default(request, hostname):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    all_instances = vyos.instance_getall()

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    
    connected = vyos.conntry(hostname)
    # show some error when not connected
    if connected == True:
        request.session['hostname'] = hostname
        instance.main = True
        instance.save()

    return redirect('config:instances')



def instance_remove(request, hostname):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    all_instances = vyos.instance_getall()

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    
    hostname_default = vyos.get_hostname_prefered(request)

    #if hostname_default != hostname:
    instance.delete()

    return redirect('config:instances')




