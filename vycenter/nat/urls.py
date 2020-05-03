from django.urls import path

from . import views

app_name = 'nat'


urlpatterns = [
    path('', views.index, name='nat-list'),
]


