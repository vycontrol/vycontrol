from django.urls import path

from . import views

app_name = 'arp'


urlpatterns = [
    path('', views.index, name='arp-list'),
]


