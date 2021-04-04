from django.urls import path

from . import views

app_name = 'dnsresolver'


urlpatterns = [
    path('', views.index, name='dnsresolver-list'),
    path('add', views.add, name='dnsresolver-add'),
    path('remove/<str:server>', views.remove, name='dnsresolver-remove'),
]


