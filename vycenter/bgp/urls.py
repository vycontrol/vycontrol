from django.urls import path

from . import views

app_name = 'bgp'


urlpatterns = [
    path('', views.index, name='bgp-list'),
]


