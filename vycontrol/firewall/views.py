from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse



import vyos



def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)



    firewall_all = vyos.get_firewall_all(hostname_default)
    if firewall_all == False:
        return redirect('firewall:firewall-create')

    for xitem in firewall_all['name']:
        if 'default-action' in firewall_all['name'][xitem]:
            firewall_all['name'][xitem]['default_action'] = firewall_all['name'][xitem]['default-action']
            del firewall_all['name'][xitem]['default-action']

    template = loader.get_template('firewall/list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all':  firewall_all,
    }   
    return HttpResponse(template.render(context, request))


def create(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    if 'name' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", request.POST['name']]}
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)

        if 'description' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "description", request.POST['description']]}
            result2 = vyos.set_config(hostname_default, cmd)
            print(result2)

        if 'action' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "default-action", request.POST['action']]}
            result3 = vyos.set_config(hostname_default, cmd)
            print(result3)

        return redirect('firewall:firewall-list')

    template = loader.get_template('firewall/create.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
    }   
    return HttpResponse(template.render(context, request))




def addrule(request, firewall_name):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    
    changed = False
    if 'action' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "action", request.POST['action']]}
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)
        changed = True

    if 'protocol' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "protocol", request.POST['protocol']]}
        result2 = vyos.set_config(hostname_default, cmd)
        print(result2)
        changed = True

    if 'destinationport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "destination", "port", request.POST['destinationport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)
        changed = True

    if 'sourceport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "source", "port", request.POST['sourceport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)        
        changed = True

    if changed == True:
        return redirect('firewall:show', firewall_name)
        

    template = loader.get_template('firewall/addrule.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
    }  
    return HttpResponse(template.render(context, request))








def firewall_removerule(request, firewall_name, firewall_rulenumber):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    firewall_rule = vyos.get_firewall_rule(hostname_default, firewall_name, firewall_rulenumber)

    if firewall_rule and firewall:
        vyos.delete_route_rule(hostname_default, firewall_name, firewall_rulenumber)

    return redirect('firewall:show', firewall_name)






def editrule(request, firewall_name, firewall_rulenumber):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    firewall_rule = vyos.get_firewall_rule(hostname_default, firewall_name, firewall_rulenumber)

    changed = False

    if 'action' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", firewall_rulenumber, "action", request.POST['action']]}
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)
        changed = True

    if 'protocol' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", firewall_rulenumber, "protocol", request.POST['protocol']]}
        result2 = vyos.set_config(hostname_default, cmd)
        print(result2)
        changed = True

    if 'destinationport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", firewall_rulenumber, "destination", "port", request.POST['destinationport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)
        changed = True

    if 'sourceport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", firewall_rulenumber, "source", "port", request.POST['sourceport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)
        changed = True        

    if changed == True:
        return redirect('firewall:firewall-list')


    template = loader.get_template('firewall/editrule.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
        'firewall_rule': firewall_rule,
        'firewall_rulenumber' : firewall_rulenumber
    }  
    return HttpResponse(template.render(context, request))






def show(request, firewall_name):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    

    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
    }   
    return HttpResponse(template.render(context, request))




def firewall_addressgroup_list(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    hostname_default = vyos.get_hostname_prefered(request)
    firewall_addressgroup = vyos.get_firewall_addressgroup(hostname_default)

    template = loader.get_template('firewall/addressgroup-list.html')
    context = { 
        'firewall_addressgroup': firewall_addressgroup,
    }   
    return HttpResponse(template.render(context, request))



def firewall_addressgroup_add(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    hostname_default = vyos.get_hostname_prefered(request)

    if request.POST.get('addresstype', None) == "single" and request.POST.get('name', None) != None and request.POST.get('address', None) != None:
        vyos.set_firewall_addressgroup_add(hostname_default, request.POST.get('name'), request.POST.get('address'))
        return redirect('firewall:firewall-addressgroup-list')
    elif request.POST.get('addresstype', None) == "range" and request.POST.get('name', None) != None and request.POST.get('address-start', None) != None and request.POST.get('address-end', None) != None:
        vyos.set_firewall_addressgroup_rangeadd(hostname_default, request.POST.get('name'), request.POST.get('address-start'), request.POST.get('address-end'))
        return redirect('firewall:firewall-addressgroup-list')



    template = loader.get_template('firewall/addressgroup-add.html')
    context = { 
    }   
    return HttpResponse(template.render(context, request))




def firewall_networkbook(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    return redirect('firewall:firewall-list')







def firewall_config(request, firewall_name):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    

    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
    }   
    return HttpResponse(template.render(context, request))



def firewall_global(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    if int(request.POST.get('allping', 0)) == 1:
        vyos.set_firewall_allping_enable(hostname_default)
    else:
        vyos.set_firewall_allping_disable(hostname_default)

    if int(request.POST.get('syncookies', 0)) == 1:
        vyos.set_firewall_syncookies_enable(hostname_default)
    else:
        vyos.set_firewall_syncookies_disable(hostname_default)

    
    return redirect('firewall:firewall-list')



def firewall_remove(request, firewall_name):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.delete_firewall(hostname_default, firewall_name)
    
    return redirect('firewall:firewall-list')

def firewall_edit(request, firewall_name):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse('registration-login'), request.path))
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    firewall = vyos.get_firewall(hostname_default, firewall_name)
    firewall['defaultaction'] = firewall['default-action']

    changed = False
    if 'description' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "description", request.POST['description']]}
        result2 = vyos.set_config(hostname_default, cmd)
        print(result2)
        changed = True

    if 'action' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "default-action", request.POST['action']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)
        changed = True

    if changed == True:
        return redirect('firewall:firewall-list')

    template = loader.get_template('firewall/edit.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_name': firewall_name,
        'firewall': firewall

    }   
    return HttpResponse(template.render(context, request))