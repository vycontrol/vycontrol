from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import vyos
import vycontrol_vyos_api as vapi
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
