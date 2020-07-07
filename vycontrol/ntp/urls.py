from django.urls import path

from . import views

app_name = 'ntp'


urlpatterns = [
    path('', views.index, name='ntp-list'),
]


