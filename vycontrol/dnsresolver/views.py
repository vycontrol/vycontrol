from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

import vyos
import vycontrol_vyos_api_lib as vapilib
import vycontrol_vyos_api as vapi

from perms import is_authenticated
from libs.vycontrol_filters import routeunpack

import perms
import validators
import viewinfo


@is_authenticated
def index(request):
    vinfo = viewinfo.prepare(request)

    dnsresolver_srv = vapi.get_dnsresolver(vinfo.hostname_default)
    dnsresolver_servers = {}
    if dnsresolver_srv.success:
        if dnsresolver_srv.data['name-server'] != None:
            dnsresolver_servers = dnsresolver_srv.data['name-server']

    context = viewinfo.context(vinfo)    
    localcontext = {
        'dnsresolver_servers' :                     dnsresolver_servers,
    }
    context.update(localcontext)

    return render(request, 'dnsresolver/list.html', context)


@is_authenticated
def add(request):
    vinfo = viewinfo.prepare(request)

    if 'server' in request.POST:
        if validators.ipv6(request.POST['server'].strip()) or validators.ipv4(request.POST['server'].strip()):
            v = vapi.set_dnsresolver(vinfo.hostname_default, request.POST['server'].strip())
            if v.success == False: 
                vinfo.msg.add_error("dnsresolver server add fail - " + v.reason)
            else:
                vinfo.msg.add_success("dnsresolver server added")
        else:
            vinfo.msg.add_error("dnsresolver server add fail - insert only IPv4 or IPv6")

    context = viewinfo.context(vinfo)    
    localcontext = {
    }
    context.update(localcontext)
    
    return render(request, 'dnsresolver/add.html', context)


@is_authenticated
def remove(request, server):
    vinfo = viewinfo.prepare(request)

    dnsresolver_srv = vapi.get_dnsresolver(vinfo.hostname_default)
    if len(dnsresolver_srv.data['name-server']) == 0:
        return redirect('dnsresolver:dnsresolver-list')

    if dnsresolver_srv.success:
        if 'name-server' in dnsresolver_srv.data:
            if validators.ipv6(server.strip()) or validators.ipv4(server.strip()):
                v = vapi.delete_dnsresolver(vinfo.hostname_default, server.strip())

    return redirect('dnsresolver:dnsresolver-list')
