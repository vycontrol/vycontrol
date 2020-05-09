from django.urls import path

from . import views

app_name = 'openvpn'


urlpatterns = [
    path('', views.index, name='openvpn-list'),
]


