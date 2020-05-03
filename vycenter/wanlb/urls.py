from django.urls import path

from . import views

app_name = 'wanlb'


urlpatterns = [
    path('', views.index, name='wanlb-list'),
]


