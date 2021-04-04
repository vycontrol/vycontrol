from django.urls import path

from . import views


app_name = 'config'

urlpatterns = [
    path('instance-change/<str:hostname>', views.instance_change, name='instance-change'),
    path('users-list', views.users_list, name='users-list'),
    path('groups-list', views.groups_list, name='groups-list'),
    path('group-add', views.group_add, name='group-add'),
    path('user-add', views.user_add, name='user-add'),
    path('instance-add', views.instance_add, name='instance-add'),
    path('instance-conntry/<str:hostname>', views.instance_conntry, name='instance-conntry'),
    path('instance-remove/<str:hostname>', views.instance_remove, name='instance-remove'),
    path('instance-changegroup/<str:hostname>', views.instance_changegroup, name='instance-changegroup'),
    path('instances', views.instances, name='instances'),

]
