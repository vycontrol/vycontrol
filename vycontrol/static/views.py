from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

import vyos
import vycontrol_messages as vmsg
import vycontrol_vyos_api_lib as vapilib
import vycontrol_vyos_api as vapi

from perms import is_authenticated
from filters.vycontrol_filters import routeunpack
import perms


@is_authenticated    
def static_list(request):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    static_dict = vyos.get_route_static(hostname_default)
    is_superuser = perms.get_is_superuser(request.user)

    static_list = []
    if static_dict :
        for s in static_dict['route']:
            static_list.append({
                'route': s,
                'nexthop': static_dict['route'][s]['next-hop'],
            })

    template = loader.get_template('static/list.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
        'static_list' : static_list,
        'username': request.user,
        'is_superuser' : is_superuser,     
    }   
    return HttpResponse(template.render(context, request))


@is_authenticated    
def static_add(request):
    msg = vmsg.msg()

    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    static_list = vyos.get_route_static(hostname_default)
    is_superuser = perms.get_is_superuser(request.user)

    if 'subnet' in request.POST and 'nexthop' in request.POST:
        v = vapi.set_route_static(hostname_default, request.POST['subnet'], request.POST['nexthop'])
        if v.success == False: 
            msg.add_error("Static route add fail - " + v.reason)
        else:
            msg.add_success("Static route added")

    ippath = vyos.ip_route(hostname_default)

    template = loader.get_template('static/add.html')
    context = { 
        'instances':                        all_instances,
        'hostname_default':                 hostname_default,
        'static_list' :                     static_list,
        'username':                         request.user,
        'is_superuser' :                    is_superuser,     
        'msg' :                             msg.get_all(),
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated    
def static_remove(request, route, nexthop):
        
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    static_list = vyos.get_route_static(hostname_default)

    print(route)
    print(routeunpack(route))


    if route and nexthop:
        return1 = vyos.delete_route_static(hostname_default, routeunpack(route), nexthop)



    return redirect('static:static-list')

