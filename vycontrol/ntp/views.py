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


@login_required
def index(request):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    ntp_srv = vapi.get_ntp(hostname_default)
    ntp_servers = {}
    if ntp_srv.success:
        if ntp_srv.data['server'] != None:
            ntp_servers = ntp_srv.data['server']

    context = {
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'ntp_servers' :                             ntp_servers,
        'is_superuser' :                            is_superuser,
    }

    return render(request, 'ntp/list.html', context)


@login_required
def add(request):
    msg = vmsg.msg()

    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    if 'server' in request.POST:
        v = vapi.set_ntp(hostname_default, request.POST['server'])
        if v.success == False: 
            msg.add_error("NTP server add fail - " + v.reason)
        else:
            msg.add_success("NTP server added")

    context = {
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'is_superuser' :                            is_superuser,
        'msg' :                                     msg.get_all(),
    }

    return render(request, 'ntp/add.html', context)


@login_required
def remove(request, server):
    hostname_default = vyos.get_hostname_prefered(request)

    ntp_srv = vapi.get_ntp(hostname_default)
    ntp_servers = {}
    if ntp_srv.success:
        if ntp_srv.data['server'] != None:
            ntp_servers = ntp_srv.data['server']

    if server in ntp_servers:
        return1 = vapi.delete_ntp(hostname_default, server)

    return redirect('ntp:ntp-list')
