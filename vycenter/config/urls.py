from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('instance_add/', views.instance_add, name='instance_add'),
    path('instance/', views.instance, name='instance'),

]
