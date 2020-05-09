from django.urls import path

from . import views

app_name = 'qos'


urlpatterns = [
    path('', views.index, name='qos-list'),
]


