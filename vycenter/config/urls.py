from django.urls import path

from . import views


app_name = 'config'

urlpatterns = [
    path('', views.index, name='index'),
    path('instance-add', views.instance_add, name='instance-add'),
    path('instances', views.instances, name='instances'),

]
