from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('instance-add', views.instance_add, name='instance-add'),
    path('instance', views.instance, name='instance'),

]
