from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('interface/<slug:interface_type>/<slug:interface_name>', views.interface, name='device-views-interface'),
]
