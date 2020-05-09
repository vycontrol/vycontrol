from django.urls import path
from django.urls import include
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import views as auth_views


import vyos

from . import views

app_name = 'accounts'






urlpatterns = [
   path('', views.index, name='accounts-index'),
   # path('', include('django.contrib.auth.urls', name='vauth-login')
]



