from django.urls import path

from . import views

app_name = 'ssh'


urlpatterns = [
    path('', views.index, name='ssh-list'),
]


