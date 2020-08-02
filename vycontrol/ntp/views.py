from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import vyos
import vycontrol_vyos_api as vapi

@login_required
def index(request):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    ntp_srv = vapi.get_ntp(hostname_default)
    context = {'instances': all_instances,
               'hostname_default': hostname_default,
               'ntp_servers': ntp_srv.data['server']}
    return render(request, 'ntp/list.html', context)
