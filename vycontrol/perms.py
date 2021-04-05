import functools

from django.shortcuts import redirect
from django.urls import reverse

from config.models import Instance
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib import auth

import vyos



def is_authenticated(func):
    @functools.wraps(func)
    def wrapper_perm(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
           return redirect('%s?next=%s' % (reverse('accounts-login'), request.path))

        # check if username is active
        user = User.objects.filter(
            username=request.user,
            is_active=True
        )
        if user.count() != 1:
            return redirect('%s?next=%s' % (reverse('accounts-login'), request.path))
        
        # check if return a valid hostname
        hostname = get_hostname_prefered(request)
        if hostname == None:
            return redirect('%s?next=%s' % (reverse('accounts-login'), request.path))

        value = func(*args, **kwargs)
        return value
    return wrapper_perm


def is_superuser(func):
    @functools.wraps(func)
    def wrapper_perm(*args, **kwargs):
        request = args[0]

        # get username    
        username = request.user
                
        # check if username is admin
        useradmin = User.objects.filter(
            username=username,
            is_active=True,
            is_superuser=True
        )
        is_admin = False
        if useradmin.count() > 0:
            is_admin = True

        if is_admin == False:
            auth.logout(request)
            return redirect('%s?next=%s' % (reverse('accounts-login'), request.path))

        value = func(*args, **kwargs)
        return value
    return wrapper_perm

def get_is_superuser(username):
    # check if username is admin
    useradmin = User.objects.filter(
        username=username,
        is_active=True,
        is_superuser=True
    )
    is_admin = False
    if useradmin.count() > 0:
        is_admin = True
    return is_admin    

def instance_getall_by_group(request):
     # get username    
    username = request.user

    # check if username is admin
    useradmin = User.objects.filter(
        username=username,
        is_active=True,
        is_superuser=True
    )
    is_admin = False
    if useradmin.count() > 0:
        is_admin = True



    if is_admin:
        instances = Instance.objects.all()
        return instances
    else:
        try:
            usergroup = Group.objects.get(user=username)
        except Group.DoesNotExist:
            return None
                    
        try:
            instances = Instance.objects.filter(group=usergroup)
            return instances
        except Instance.DoesNotExist:
            pass

    return None



def instance_getall():
    instances = Instance.objects.all()
    return instances

def user_has_hostname_access(username, hostname):
    # superuser has access too all hostnames
    if get_is_superuser(username) == True:
        return True

    # get usergroup - VyControl groups is one to one
    try:
        usergroup = Group.objects.get(user=username)
    except Group.DoesNotExist:
        # if user has no group return false because only groups has access to instances
        return False

    try:
        instance = Instance.objects.get(hostname=hostname, group=usergroup)
        if instance.count() == 1:
            return True
    except Instance.DoesNotExist:
        return False

    return False


def get_hostname_prefered(request):
    # get username    
    username = request.user
    hostname = None

    # get usergroup - VyControl groups is one to one
    try:
        usergroup = Group.objects.get(user=username, active=True)
    except Group.DoesNotExist:
        usergroup = None

    # check if username is admin
    useradmin = User.objects.filter(
        username=username,
        is_active=True,
        is_superuser=True
    )
    is_admin = False
    if useradmin.count() > 0:
        is_admin = True

    # get session hostname and validate if group has permission
    if request.session.get('hostname', None) != None and usergroup != None:
        hostname = request.session.get('hostname', None)
        try:
            instance = Instance.objects.get(hostname=hostname, group=usergroup)
            return instance.hostname
        except Instance.DoesNotExist:
            pass


    # if we have no hostname yet try to get the default one from database
    if hostname == None:
        try:
            instance = Instance.objects.get(main=True, group=usergroup)
            request.session['hostname'] = instance.hostname
            return instance.hostname
        except Instance.DoesNotExist:
            pass

        # if superuser get any instance
        if is_admin:
            try:
                instance = Instance.objects.all()
                for i in instance:
                    request.session['hostname'] = i.hostname
                    return i.hostname


            except Instance.DoesNotExist:
                pass
   
    return hostname