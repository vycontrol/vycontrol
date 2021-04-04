from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group

import pprint
import vyos

from .models import Instance

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from django.template.defaultfilters import register


from perms import is_authenticated
import perms

from libs.vycontrol_filters import get_item



@is_authenticated
def index(request):

    is_superuser = perms.get_is_superuser(request.user)
 
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    for instance in all_instances:
        if group == None:
            all_instance[instance]['group'] = "admin"
            
    hostname_default = vyos.get_hostname_prefered(request)


    template = loader.get_template('config/instance.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@perms.is_superuser
@is_authenticated
def users_list(request):
    is_superuser = perms.get_is_superuser(request.user)


    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)
    users = User.objects.all()
    groups = Group.objects.all()

    group_show = []
    for group in groups:
        if group.name != "admin":
            group_show.append(group.name)


    has_group_add = False
    for el in request.POST:


        if el.startswith('group-') and request.POST[el]:
            pos = el.split("-", 1)
            
            el_username = pos[1]
            el_groupname = request.POST[el]

           
            # test also if username is member of admin or superuser, than this one should not being no group
            if el_groupname not in ['admin']:

                try:
                    el_userid = User.objects.get(username=el_username) 
                except User.DoesNotExist:
                    return redirect('config:users_list')

                try:
                    if el_userid.groups.exists():
                        for g in el_userid.groups.all():
                            el_userid.groups.remove(g)
                except Group.DoesNotExist:
                    return redirect('config:users_list')



                if el_groupname == "--remove--":
                    has_group_add = has_group_add  + 1
                else:
                    el_groupadd = Group.objects.get(name=el_groupname) 
                    el_groupadd.user_set.add(el_userid)
                    has_group_add = has_group_add  + 1

    if has_group_add > 0:
        return redirect('config:users-list')


    user_groups = {}
    for user in users:
        #print(user.email)
        user_groups_list = user.groups.all()
        if len(user_groups_list) > 0:
            user_groups[str(user)] = str(user_groups_list[0])
        else:
            user_groups[str(user)] = None

    template = loader.get_template('config/users_list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'users' : users,
        'groups': group_show,
        'user_groups': user_groups,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@perms.is_superuser
@is_authenticated
def groups_list(request):
    is_superuser = perms.get_is_superuser(request.user)

    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)
    groups = Group.objects.all()


    template = loader.get_template('config/groups_list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'groups' : groups,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def instances(request):
    is_superuser = perms.get_is_superuser(request.user)
        
    all_instances = perms.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    print(all_instances)

    if hostname_default == None:
        if all_instances.count() > 0:
            for i in all_instances:
                pprint.pprint(i.hostname)
                instance_default(request, i.hostname)
                
        else:
            return redirect('config:instance-add')

    groups = Group.objects.all()


    template = loader.get_template('config/instances.html')
    context = { 
        'instances': all_instances,
        'hostname_default': hostname_default,
        'groups' : groups,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@perms.is_superuser
@is_authenticated
def instance_add(request):
    is_superuser = perms.get_is_superuser(request.user)
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)

    if len(request.POST) > 0:
        instance = Instance()
        instance.alias = request.POST['alias']
        instance.hostname = request.POST['hostname']
        instance.port = request.POST['port']
        instance.key = request.POST['key']
        if 'https' in request.POST:
            instance.https = request.POST['https']
        else:
            instance.https = False
        instance_id = instance.save()
        return redirect('config:instances')
    else:
        instance_id = 0

    template = loader.get_template('config/instance_add.html')
    context = { 
        'hostname_default': hostname_default,
        'instance_id': instance_id,
        'instances': all_instances,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@perms.is_superuser
@is_authenticated
def group_add(request):
    is_superuser = perms.get_is_superuser(request.user)
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)

    error_message = None

    if len(request.POST) > 0 and 'name' in request.POST:
        try:
            group_get = Group.objects.get(name=request.POST['name'])       
            error_message = 'Group already exists'
        except Group.DoesNotExist:
            group_create = Group(name=request.POST['name'])
            group_create.save()
            return redirect('config:groups-list')
    else:
        instance_id = 0

    template = loader.get_template('config/group_add.html')
    context = { 
        'hostname_default': hostname_default,
        'instance_id': instance_id,
        'instances': all_instances,
        'error_message' : error_message,
        'username': request.user,
        'is_superuser' : is_superuser,
    }
    return HttpResponse(template.render(context, request)) 

@perms.is_superuser
@is_authenticated    
def user_add(request):
    is_superuser = perms.get_is_superuser(request.user)

    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)

    error_message = None

    count = 0
    name = ''
    if 'name' in request.POST:
        name = request.POST['name']
        count += 1

    username = ''
    if 'username' in request.POST:
        username = request.POST['username']
        count += 1

    password = ''
    if 'password' in request.POST:
        password = request.POST['password']
        count += 1

    email = ''
    if 'email' in request.POST:
        email = request.POST['email']                        
        count += 1

    if count >= 4:
        try:
            user = User.objects.get(username=username)       
            error_message = 'Username already exists'
        except User.DoesNotExist:
            user_create = User(
                username=username,
                email=email,
                password=password,
                last_name=name
            )
            user_create.save()
            return redirect('config:users-list')


    template = loader.get_template('config/user_add.html')
    context = { 
        'hostname_default': hostname_default,
        'instances': all_instances,
        'error_message' : error_message,
        'name' : name,
        'username' : username,
        'password' : password,
        'email' : email,
        'username': request.user,
        'is_superuser' : is_superuser,

    }   
    return HttpResponse(template.render(context, request))    

@is_authenticated
def instance_conntry(request, hostname):
    is_superuser = perms.get_is_superuser(request.user)
       
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)

    if perms.user_has_hostname_access(request.user, hostname) == False:
        return redirect('config:instances')

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    connected = vyos.conntry(hostname)
    if connected == True:
        request.session['hostname'] = hostname


    template = loader.get_template('config/instance_conntry.html')
    context = { 
        'instance': instance,
        "connected": connected,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

# get default instance or set default instance 
@is_authenticated
def instance_change(request, hostname = False):
        
    all_instances = vyos.instance_getall_by_group(request)

    #method = None  
    if hostname != "__none__":
        #method = "param"
        pass
    elif hostname == "__none__":
        #method = "get"
        hostname = request.POST.get('vyos-id', False)
 
    # permcheck
    if hostname != False:
        if perms.user_has_hostname_access(request.user, hostname) == False:
            return redirect('config:instances')

        try:
            instance = Instance.objects.get(hostname=hostname)
        except Instance.DoesNotExist:
            print("instance not exists: " + str(hostname))
            return redirect('config:instances')    

        if instance:
            connected = vyos.conntry(hostname)
            # show some error when not connected
            if connected == True:
                request.session['hostname'] = hostname
                instance.main = True
                instance.save()

    return redirect('config:instances')    

@perms.is_superuser
@is_authenticated
def instance_remove(request, hostname):
        
    all_instances = vyos.instance_getall_by_group(request)

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    
    hostname_default = vyos.get_hostname_prefered(request)

    #if hostname_default != hostname:
    instance.delete()

    return redirect('config:instances')

@perms.is_superuser
@is_authenticated
def instance_changegroup(request, hostname):
       
    all_instances = vyos.instance_getall_by_group(request)

    group_name = request.POST.get('group')
    print(group_name, hostname)

    if group_name == "__admin__":
        instance = Instance.objects.get(hostname=hostname)
        instance.group = None
        instance.save()
    else:
        group = Group.objects.get(name=group_name)
        instance = Instance.objects.get(hostname=hostname)
        instance.group = group
        instance.save()


    return redirect('config:instances')







