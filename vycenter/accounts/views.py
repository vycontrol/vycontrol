from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.views.generic.base import TemplateView
from django.conf import settings


from django.contrib.auth.models import User

import vyos




def index(request):
    users_admin = User.objects.filter(
        is_active=True,
        is_superuser=True
    )

    if users_admin.count() > 0:
        if request.user.is_authenticated:
            return redirect('interface:interface-list')
        else:
            return redirect('registration-login')
    else:
        if 'username' in request.POST and 'password' in request.POST:
            user = User.objects.create_superuser(username=request.POST['username'], password=request.POST['password'])
            user.save()
            return redirect('registration-login')
         
    template = loader.get_template('registration/start.html')
    context = { 
        'users_admin': users_admin.all()
    }   
    return HttpResponse(template.render(context, request))
