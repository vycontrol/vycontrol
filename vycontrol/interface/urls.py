from django.urls import path

from . import views

app_name = 'interface'

urlpatterns = [
    path('', views.index, name='interface-list'),
    path('interface-show/<slug:interface_type>/<str:interface_name>', views.interface_show, name='interface-show'),
    path('interface-firewall/<slug:interface_type>/<str:interface_name>', views.interface_firewall, name='interface-firewall'),
    path('interface-set-firewall/<slug:interface_type>/<str:interface_name>', views.interface_set_firewall, name='interface-set-firewall'),
    path('interface-set/<slug:interface_type>/<str:interface_name>', views.interface_set, name='interface-set'),
    path('interface-delete/<slug:interface_type>/<str:interface_name>/<str:interface_vif>', views.interface_delete, name='interface-delete'),
    path('interface-delete/<slug:interface_type>/<str:interface_name>', views.interface_delete, name='interface-delete'),
    path('interface-add', views.interface_add, name='interface-add'),
    path('interface-add-vlan/<slug:interface_type>/<str:interface_name>', views.interface_add_vlan, name='interface-add-vlan'),
    path('interface-add-vlan', views.interface_add_vlan, name='interface-add-vlan'),


]
