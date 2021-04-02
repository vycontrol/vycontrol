from django.urls import path

from . import views

app_name = 'ntp'


urlpatterns = [
    path('', views.index, name='ntp-list'),
    path('add', views.add, name='ntp-add'),
    path('remove/<str:server>', views.remove, name='ntp-remove'),
]


