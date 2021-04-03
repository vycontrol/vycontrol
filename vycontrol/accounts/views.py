from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.views.generic.base import TemplateView
from django.conf import settings
from django.urls import reverse


from django.contrib.auth.models import User

import vyos
from perms import is_authenticated
import perms
import vycontrol_vyos_api as vapi
from libs.vycontrol_validators import *
import vycontrol_messages as vmsg

from config.models import Instance

import pprint
import validators



def index(request):
    users_admin = User.objects.filter(
        is_active=True,
        is_superuser=True
    )

    if users_admin.count() > 0:
        if request.user.is_authenticated:
            return redirect('interface:interface-list')
        else:
            return redirect('accounts-login')
    else:
        if 'username' in request.POST and 'password' in request.POST:
            user = User.objects.create_superuser(username=request.POST['username'], email='', password=request.POST['password'])
            user.save()
            return redirect('%s?next=%s' % (reverse('registration-login'), '/config/instance-add'))
    template = loader.get_template('accounts/start.html')
    context = { 
        'users_admin': users_admin.all()
    }   
    return HttpResponse(template.render(context, request))



@is_authenticated    
def profile(request):
    all_instances = vyos.instance_getall()
    is_superuser = perms.get_is_superuser(request.user)
    hostname_default = vyos.get_hostname_prefered(request)
    msg = vmsg.msg()

    user = User.objects.get(
        username=request.user,
        is_active=True
    )
    
    if request.POST.get('email', None) != None:
        email_new = request.POST.get('email').strip()
        if validators.email(email_new):
            user.email = email_new
            user.save()
    
    if request.POST.get('pass1', None) != None and request.POST.get('pass2', None) != None:
        if request.POST.get('pass1') == request.POST.get('pass2'):
            pass_new = request.POST.get('pass1').strip()
            if pass_new != '':
                user.set_password(pass_new)
                user.save()



    template = loader.get_template('accounts/profile.html')
    context = { 
        'instances':            all_instances,
        'hostname_default':     hostname_default,
        'username':             request.user,      
        'is_superuser':         is_superuser, 
        'msg':                  msg.get_all(),
        'user':                 user,


    }   
    return HttpResponse(template.render(context, request))
