from django.urls import path

from . import views

app_name = 'firewall'


urlpatterns = [
    path('', views.index, name='firewall-list'),
    path('show/<str:firewall_name>', views.show, name='show'),
    path('addrule/<str:firewall_name>', views.addrule, name='addrule'),
]


