from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import vyos
import vycontrol_vyos_api as vapi
import vycontrol_messages as vmsg
import perms
import validators

@login_required
def index(request):
    all_instances = vyos.instance_getall()
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
    }

    return render(request, 'dnsresolver/list.html', context)


@login_required
def add(request):
    msg = vmsg.msg()

    all_instances = vyos.instance_getall()
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
        'is_superuser' :                            is_superuser,
        'msg' :                                     msg.get_all(),
    }

    return render(request, 'dnsresolver/add.html', context)


@login_required
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
