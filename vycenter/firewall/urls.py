from django.urls import path

from . import views

app_name = 'firewall'



urlpatterns = [
    path('', views.index, name='firewall-list'),
    path('show/<str:firewall_name>', views.show, name='show'),
    path('firewall-create', views.create, name='firewall-create'),
    path('firewall-remove/<str:firewall_name>', views.firewall_remove, name='firewall-remove'),
    path('firewall-edit/<str:firewall_name>', views.firewall_edit, name='firewall-edit'),
    path('addrule/<str:firewall_name>', views.addrule, name='addrule'),
    path('editrule/<str:firewall_name>/<str:firewall_rulenumber>', views.editrule, name='editrule'),
    path('firewall-removerule/<str:firewall_name>/<str:firewall_rulenumber>', views.firewall_removerule, name='firewall-removerule'),    

]


