"""vycontrol URL Configuration

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
from django.urls import path, re_path
from accounts import views as accounts_views


app_name = 'vycontrol'

urlpatterns = [
    path('', accounts_views.index, name='main-page'),
    path('accounts/', include('accounts.urls')),
    path('config/', include('config.urls')),
    path('admin/', admin.site.urls, name="django-admin"),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name="accounts-login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name="accounts-logout"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name = 'accounts/password_reset.html'), name ='reset_password'),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name = 'accounts/password_reset_sent.html'), name ='password_reset_done'),
    path('password_reset_token/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = 'accounts/password_reset_token.html'), name ='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'accounts/password_reset_complete.html'), name ='password_reset_complete'),
    path('static/', include('static.urls')),
    path('interface/', include('interface.urls')),
    path('firewall/', include('firewall.urls')),
    path('ntp/', include('ntp.urls')),
    path('dnsresolver/', include('dnsresolver.urls')),
]
