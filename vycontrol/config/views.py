from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.generic.base import TemplateView
from django.conf import settings
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from config.models import Instance

import vyos
import perms
import vapi
import vmsg
import viewinfo
import validators
from perms import is_authenticated

from libs.vycontrol_validators import *
from django.template.defaultfilters import register
from libs.vycontrol_filters import get_item

@perms.is_superuser
@is_authenticated
def users_list(request):
    vinfo = viewinfo.prepare(request)

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

    context = viewinfo.context(vinfo)    
    localcontext = {
        'users' : users,
        'groups': group_show,
        'user_groups': user_groups,
    }
    context.update(localcontext)

    return render(request, 'config/users_list.html', context)


@perms.is_superuser
@is_authenticated
def groups_list(request):
    vinfo = viewinfo.prepare(request, title="Groups list")

    groups = Group.objects.all()

    context = viewinfo.context(vinfo)    
    localcontext = {
        'groups' : groups,
    }
    context.update(localcontext)

    return render(request, 'config/groups_list.html', context)   


@is_authenticated
def instances(request):
    vinfo = viewinfo.prepare(request, "Instances List")

    if vinfo.hostname_default == None:
        if vinfo.all_instances.count() > 0:
            for i in vinfo.all_instances:
                instance_default(request, i.hostname)
                
        else:
            return redirect('config:instance-add')

    groups = Group.objects.filter(active=True)


    context = viewinfo.context(vinfo)    
    localcontext = {
        'groups' : groups,
    }
    if len(vinfo.all_instances) == 0:
        localcontext['noinstance'] = True
        
    context.update(localcontext)

    return render(request, 'config/instances.html', context)   


@perms.is_superuser
@is_authenticated
def instance_add(request):
    vinfo = viewinfo.prepare(request)

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

    context = viewinfo.context(vinfo)    
    localcontext = {
    }
    context.update(localcontext)

    return render(request, 'config/instance_add.html', context)  

@perms.is_superuser
@is_authenticated
def group_add(request):
    vinfo = viewinfo.prepare(request)

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

    context = viewinfo.context(vinfo)    
    localcontext = {
        'error_message' : error_message,
    }
    context.update(localcontext)

    return render(request, 'config/group_add.html', context) 

@perms.is_superuser
@is_authenticated    
def user_add(request):
    vinfo = viewinfo.prepare(request)

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

    context = viewinfo.context(vinfo)    
    localcontext = {
        'error_message' :   error_message,
        'name' :            name,
        'username' :        username,
        'password' :        password,
        'email' :           email,
    }
    context.update(localcontext)

    return render(request, 'config/user_add.html', context) 

@perms.is_superuser
@is_authenticated    
def user_inactivate(request, username):
    vinfo = viewinfo.prepare(request)
    if validator_letters_numbers(username):
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()

    return redirect('config:users-list')

@perms.is_superuser
@is_authenticated    
def user_activate(request, username):
    vinfo = viewinfo.prepare(request)
    if validator_letters_numbers(username):
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()

    return redirect('config:users-list')

    
@perms.is_superuser
@is_authenticated    
def user_edit(request, username):
    vinfo = viewinfo.prepare(request)
    if validator_letters_numbers(username):
        user = User.objects.get(username=username)
        if request.POST.get('email', None) != None:
            email_new = request.POST.get('email').strip()

            if validators.email(email_new):
                user.email = email_new
                user.save()
    
        if request.POST.get('pass1', None) != None and request.POST.get('pass2', None) != None:
            if request.POST.get('pass1') == request.POST.get('pass2'):
                pass_new = request.POST.get('pass1').strip()
                if pass_new != '':
                    user.set_password(pass_new)
                    user.save()
    else:
        return redirect('config:users-list')

    context = viewinfo.context(vinfo)    
    localcontext = {
        'user':             user
    }
    context.update(localcontext)

    return render(request, 'config/user_edit.html', context) 


@is_authenticated
def instance_conntry(request, hostname):
    vinfo = viewinfo.prepare(request)

    if perms.user_has_hostname_access(request.user, hostname) == False:
        return redirect('config:instances')

    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    connected = vyos.conntry(hostname)
    if connected == True:
        request.session['hostname'] = hostname

    context = viewinfo.context(vinfo)    
    localcontext = {
        'instance':         instance,
        "connected":        connected,
    }
    context.update(localcontext)

    return render(request, 'config/instance_conntry.html', context) 

# get default instance or set default instance 
@is_authenticated
def instance_change(request, hostname = False):
    vinfo = viewinfo.prepare(request)

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
    vinfo = viewinfo.prepare(request)

    instance = Instance.objects.get(hostname=hostname)
    instance.delete()

    return redirect('config:instances')

@perms.is_superuser
@is_authenticated
def instance_changegroup(request, hostname):     
    vinfo = viewinfo.prepare(request)

    group_name = request.POST.get('group')

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

@perms.is_superuser
@is_authenticated
def instance_edit(request, hostname):

    if not validators.domain(hostname) and not validators.ipv4(hostname):
        return redirect('config:instances')

    vinfo = viewinfo.prepare(request, "Instance edit " + hostname)

    try:
        instance = Instance.objects.get(hostname=hostname)
    except Instance.DoesNotExist:
        return redirect('config:instances')

    if len(request.POST) > 0:
        error = False

        instance.alias = request.POST.get('alias').strip()
        instance.hostname = request.POST.get('hostname').strip()
        instance.port = request.POST.get('port').strip()
        try:
            port_number = int(instance.port)
        except:
            port_number = 0
        instance.key = request.POST.get('key').strip()

        if 'https' in request.POST:
            instance.https = True
        else:
            instance.https = False

        if not validator_letters_numbers(instance.alias):
            error = True
            vinfo.msg.add_error("Alias need to be letters and numbers only")
        if not validators.domain(instance.hostname) and not validators.ipv4(instance.hostname):
            error = True
            vinfo.msg.add_error("Hostname need to be only domain or ipv4")
        if not validator_letters_numbers(instance.key):
            error = True
            vinfo.msg.add_error("Key need to be letters and numbers only")
        if not validators.between(port_number, 1, 65535):
            error = True
            vinfo.msg.add_error("Port need to be between 1 and 65535")

        if error == False:
            instance.save()

    context = viewinfo.context(vinfo)    
    localcontext = {
        'instance':         instance,
    }
    context.update(localcontext)

    return render(request, 'config/instance_edit.html', context) 


@perms.is_superuser
@is_authenticated    
def group_inactivate(request, group_name):
    vinfo = viewinfo.prepare(request)
    if validator_group(group_name):
        group = Group.objects.get(name=group_name)
        group.active = False
        group.save()

    return redirect('config:groups-list')

@perms.is_superuser
@is_authenticated    
def group_activate(request, group_name):
    vinfo = viewinfo.prepare(request)
    if validator_group(group_name):
        group = Group.objects.get(name=group_name)
        group.active = True
        group.save()

    return redirect('config:groups-list')


@perms.is_superuser
@is_authenticated    
def group_edit(request, group_name):
    vinfo = viewinfo.prepare(request, title="Group edit")

    if validator_group(group_name):
        group = Group.objects.get(name=group_name)

        if request.POST.get('name', None) != None:
            newname = request.POST.get('name').strip()

            if validator_group(newname):
                group.name = newname
                group.save()
            else:
                vinfo.msg.add_error('Group name only accept letters, numbers and _-.')
            
    else:
        return redirect('config:groups-list')

    context = viewinfo.context(vinfo)    
    localcontext = {
        'group':             group
    }
    context.update(localcontext)

    return render(request, 'config/group_edit.html', context)     