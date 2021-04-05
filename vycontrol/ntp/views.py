from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import vyos
import vapi
import vmsg
import perms
import validators
from perms import is_authenticated


@is_authenticated
def index(request):
    all_instances = perms.instance_getall_by_group(request)
    hostname_default = perms.get_hostname_prefered(request)
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
        'username':                                 request.user,
        'is_superuser' :                            is_superuser,
    }

    return render(request, 'ntp/list.html', context)


@is_authenticated
def add(request):
    msg = vmsg.msg()

    all_instances = perms.instance_getall_by_group(request)
    hostname_default = perms.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    if 'server' in request.POST:
        if validators.ipv6(request.POST['server'].strip()) or validators.ipv4(request.POST['server'].strip()) or validators.domain(request.POST['server'].strip()):
            v = vapi.set_ntp(hostname_default, request.POST['server'].strip())
            if v.success == False: 
                msg.add_error("NTP server add fail - " + v.reason)
            else:
                msg.add_success("NTP server added")
        else:
            msg.add_error("ntp server add fail - insert only domains or IPv4 or IPv6")

    context = {
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'is_superuser' :                            is_superuser,
        'username':                                 request.user,
        'msg' :                                     msg.get_all(),
    }

    return render(request, 'ntp/add.html', context)


@is_authenticated
def remove(request, server):
    hostname_default = perms.get_hostname_prefered(request)

    ntp_servers = vapi.get_ntp(hostname_default)

    if len(ntp_servers.data['name-server']) == 0:
        return redirect('ntp:ntp-list')

    if ntp_servers.success:
        if 'server' in ntp_servers.data:
            if validators.ipv6(server.strip()) or validators.ipv4(server.strip()) or validators.domain(server.strip()):
                v = vapi.delete_ntp(hostname_default, server.strip())

    return redirect('ntp:ntp-list')
