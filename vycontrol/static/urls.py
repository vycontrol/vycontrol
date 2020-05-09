from django.urls import path

from . import views

app_name = 'static'


urlpatterns = [
    path('', views.static_list, name='static-list'),
    path('remove/<str:route>/<str:nexthop>', views.static_remove, name='static-remove'),
    path('add', views.static_add, name='static-add'),


]


