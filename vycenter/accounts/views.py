from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth import authenticate


import vyos



def index(request):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    if 'username' in request.POST and 'password' in request.POST:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            # A backend authenticated the credentials
            return redirect('firewall:firewall-list')
        else:
            pass



    template = loader.get_template('vauth/login.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))

