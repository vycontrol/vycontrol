"""vycenter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings

def reload_urlconf(self):
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    return import_module(settings.ROOT_URLCONF)

import pprint

from . import views

from django.contrib.auth import views as auth_views


app_name = 'vycenter'

urlpatterns = [
    path('', include('accounts.urls')),
    path('config/', include('config.urls')),
    path('dashboard/', include('dashboard.urls')),
    #path('', views.vycenter_login, name='vycenter-login'),
    path('admin/', admin.site.urls, name="django-admin"),
    #path('change-password/', auth_views.PasswordChangeView.as_view()),
    path('login/', auth_views.LoginView.as_view(), name="registration-login"),
    path('logout/', auth_views.LogoutView.as_view(), name="registration-logout"),



    path('interface/', include('interface.urls')),

    path('firewall/', include('firewall.urls')),
    path('static/', include('static.urls')),
    path('arp/', include('arp.urls')),
    path('bgp/', include('bgp.urls')),
    path('dhcp/', include('dhcp.urls')),
    path('ipsec/', include('ipsec.urls')),
    path('nat/', include('nat.urls')),
    path('openvpn/', include('openvpn.urls')),
    path('ospf/', include('ospf.urls')),
    path('qos/', include('qos.urls')),
    path('ssh/', include('ssh.urls')),
    path('wanlb/', include('wanlb.urls')),
]



