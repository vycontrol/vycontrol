from django.urls import path

from . import views

app_name = 'dhcp'


urlpatterns = [
    path('', views.index, name='dhcp-list'),
]


