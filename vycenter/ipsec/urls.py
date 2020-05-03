from django.urls import path

from . import views

app_name = 'ipsec'


urlpatterns = [
    path('', views.index, name='ipsec-list'),
]


