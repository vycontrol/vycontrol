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
from libs.vycontrol_filters import routeunpack
import perms

import validators


@is_authenticated
def index(request):
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    dnsresolver_srv = vapi.get_dnsresolver(hostname_default)
    dnsresolver_servers = {}
    if dnsresolver_srv.success:
        if dnsresolver_srv.data['name-server'] != None:
            dnsresolver_servers = dnsresolver_srv.data['name-server']

    context = {
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'dnsresolver_servers' :                     dnsresolver_servers,
        'is_superuser' :                            is_superuser,
        'username':                                 request.user,
    }

    return render(request, 'dnsresolver/list.html', context)


@is_authenticated
def add(request):
    msg = vmsg.msg()

    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    if 'server' in request.POST:
        if validators.ipv6(request.POST['server'].strip()) or validators.ipv4(request.POST['server'].strip()):
            v = vapi.set_dnsresolver(hostname_default, request.POST['server'].strip())
            if v.success == False: 
                msg.add_error("dnsresolver server add fail - " + v.reason)
            else:
                msg.add_success("dnsresolver server added")
        else:
            msg.add_error("dnsresolver server add fail - insert only IPv4 or IPv6")

    context = {
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'username':                                 request.user,
        'is_superuser' :                            is_superuser,

        'msg' :                                     msg.get_all(),
    }

    return render(request, 'dnsresolver/add.html', context)


@is_authenticated
def remove(request, server):
    hostname_default = vyos.get_hostname_prefered(request)

    dnsresolver_srv = vapi.get_dnsresolver(hostname_default)
    if len(dnsresolver_srv.data['name-server']) == 0:
        return redirect('dnsresolver:dnsresolver-list')

    if dnsresolver_srv.success:
        if 'name-server' in dnsresolver_srv.data:
            if validators.ipv6(server.strip()) or validators.ipv4(server.strip()):
                v = vapi.delete_dnsresolver(hostname_default, server.strip())

    return redirect('dnsresolver:dnsresolver-list')
