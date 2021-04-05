from django.urls import path

from . import views


app_name = 'config'

urlpatterns = [
    path('users-list', views.users_list, name='users-list'),
    path('user-inactivate/<str:username>', views.user_inactivate, name='user-inactivate'),
    path('user-activate/<str:username>', views.user_activate, name='user-activate'),
    path('user-edit/<str:username>', views.user_edit, name='user-edit'),
    path('user-add', views.user_add, name='user-add'),

    path('groups-list', views.groups_list, name='groups-list'),
    path('group-add', views.group_add, name='group-add'),
    path('group-edit/<str:group_name>', views.group_edit, name='group-edit'),
    path('group-activate/<str:group_name>', views.group_activate, name='group-activate'),
    path('group-inactivate/<str:group_name>', views.group_inactivate, name='group-inactivate'),

    path('instance-change/<str:hostname>', views.instance_change, name='instance-change'),
    path('instance-add', views.instance_add, name='instance-add'),
    path('instance-edit/<str:hostname>', views.instance_edit, name='instance-edit'),
    path('instance-conntry/<str:hostname>', views.instance_conntry, name='instance-conntry'),
    path('instance-remove/<str:hostname>', views.instance_remove, name='instance-remove'),
    path('instance-changegroup/<str:hostname>', views.instance_changegroup, name='instance-changegroup'),
    path('instances', views.instances, name='instances'),

]
