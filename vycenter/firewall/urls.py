from django.urls import path

from . import views

app_name = 'firewall'


urlpatterns = [
    path('', views.index, name='firewall-list'),
    path('show/<str:name>', views.show, name='show'),
]


