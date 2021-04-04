from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.generic.base import TemplateView
from django.conf import settings
from django.urls import reverse


from django.contrib.auth.models import User
from config.models import Instance

import vyos
import perms
import vapi
import vmsg
import viewinfo
import validators
from perms import is_authenticated
from libs.vycontrol_validators import *



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
    context = { 
        'users_admin': users_admin.all(),
    }   
    return render(request, 'accounts/start.html', context)



@is_authenticated    
def profile(request):
    vinfo = viewinfo.prepare(request)
    
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

    context = viewinfo.context(vinfo)    
    localcontext = {
        'user':                 user,
    }
    context.update(localcontext)

    return render(request, 'accounts/profile.html', context)
