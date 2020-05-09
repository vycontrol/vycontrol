from django.urls import path

from . import views

app_name = 'ospf'


urlpatterns = [
    path('', views.index, name='ospf-list'),
]


