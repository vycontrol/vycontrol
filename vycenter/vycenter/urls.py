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

from . import views


app_name = 'vycenter'


urlpatterns = [
    path('interface/', include('interface.urls')),
    path('config/', include('config.urls')),
    path('dashboard/', include('dashboard.urls')),
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
    path('', views.vycenter_login, name='vycenter-login'),
]
