from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect


import vyos



def index(request):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall_all = vyos.get_firewall_all(hostname_default)

    template = loader.get_template('firewall/list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all':  firewall_all
    }   
    return HttpResponse(template.render(context, request))



def show(request, firewall_name):
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



def addrule(request, firewall_name):
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    
    if 'action' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "action", request.POST['action']]}
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)

    if 'protocol' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "protocol", request.POST['protocol']]}
        result2 = vyos.set_config(hostname_default, cmd)
        print(result2)

    if 'destinationport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "destination", "port", request.POST['destinationport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)

    if 'sourceport' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "rule", request.POST['rulenumber'], "source", "port", request.POST['sourceport']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)        



    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
    }  
    return HttpResponse(template.render(context, request))







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


