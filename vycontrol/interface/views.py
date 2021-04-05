from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.template.defaultfilters import register


import vyos
from perms import is_authenticated
import perms
import vapi
from libs.vycontrol_validators import *
import vmsg

from config.models import Instance

import pprint


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@is_authenticated    
def index(request):
    
    hostname_default = perms.get_hostname_prefered(request)
    all_instances = perms.instance_getall_by_group(request)
    firewall_all = vyos.get_firewall_all(hostname_default)
    interfaces = vyos.get_interfaces(hostname_default)
    is_superuser = perms.get_is_superuser(request.user)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)

    interface_firewall_in = {}
    interface_firewall_out = {}

    interface_address = {}
    firewall_names = []


    # set interface_alias in format eth0 if has not vif and eth0.vlan if has vlan
    for iname in interfaces_all_names:
        if 'vif' in iname:
            iname['interface_alias'] = "{interface_name}.{vif}".format(interface_name=iname['interface_name'], vif=iname['vif'])
        else:
            iname['interface_alias'] = iname['interface_name']


    # create firewall_in and firewall_out vars
    for interface_type in interfaces:
        for interface_name in interfaces[interface_type]:
            try:
                interface_firewall_in[interface_name] = interfaces[interface_type][interface_name]['firewall']['in']['name']
            except:
                pass
            try:
                interface_firewall_out[interface_name] = interfaces[interface_type][interface_name]['firewall']['out']['name']
            except:
                pass

            if interface_name not in interface_address:
                interface_address[interface_name] = []
            try:
                interface_address[interface_name].append(interfaces[interface_type][interface_name]['address'])
            except:
                pass


            if 'vif' in interfaces[interface_type][interface_name]:
                for vif in interfaces[interface_type][interface_name]['vif']:
                    interface_name_full = "{interface_name}.{vif}".format(interface_name=interface_name, vif=vif)
                    try:
                        interface_firewall_in[interface_name_full] = interfaces[interface_type][interface_name]['vif'][vif]['firewall']['in']['name']
                    except:
                        pass
                    try:
                        interface_firewall_out[interface_name_full] = interfaces[interface_type][interface_name]['vif'][vif]['firewall']['out']['name']
                    except:
                        pass

                    if interface_name_full not in interface_address:
                        interface_address[interface_name_full] = []
                    try:
                        interface_address[interface_name_full].append(interfaces[interface_type][interface_name]['vif'][vif]['address'])
                    except:
                        pass


    # put all information in a single var: interface_all_names
    for iname in interfaces_all_names:
        if 'vif' in iname:
            ialias = "{interface_name}.{vif}".format(interface_name=iname['interface_name'], vif=iname['vif'])
        else:
            ialias = iname['interface_name']

        if ialias in interface_firewall_out:
            iname['firewall_out'] = interface_firewall_out[ialias]

        if ialias in interface_firewall_in:
            iname['firewall_in'] = interface_firewall_in[ialias]

        if ialias in interface_address:
            iname['address'] = interface_address[ialias]


    if 'name' in firewall_all:
        for fname in firewall_all['name']:
            firewall_names.append(fname)

    # create a dict
    interfaces_all_names_dict = {}
    for iname in interfaces_all_names:
        if 'vif' in iname:
            ialias = "{interface_name}.{vif}".format(interface_name=iname['interface_name'], vif=iname['vif'])
        else:
            ialias = iname['interface_name']

        interfaces_all_names_dict[ialias] = iname



    fw_changed = False
    for el in request.POST:
        interface_vif = None

        if el.startswith('firewall-ipv4-in'):
            pos = el.split(".")
            
            interface_type = pos[1]
            interface_name = pos[2]

            if len(pos) >= 4:
                interface_vif = pos[3]
                ialias = "{interface_name}.{vif}".format(interface_name=interface_name, vif=interface_vif)
            else:
                ialias = interface_name


            firewall_name = request.POST[el]
            if firewall_name == "--remove--":
                if 'firewall_in' in interfaces_all_names_dict[ialias]:
                    v = vapi.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "in", interface_vif)
                    #print("@@@@@@@@@@@@@@@@@ in delete", hostname_default, interface_type, interface_name, "in", firewall_name, interface_vif)
                else:
                    pass
                    #print("@@@@@ not 1", interfaces_all_names_dict[ialias], firewall_name)
            else:
                if 'firewall_in' not in interfaces_all_names_dict[ialias] or interfaces_all_names_dict[ialias]['firewall_in'] != firewall_name:
                    v = vapi.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "in", firewall_name, interface_vif)         
                    #print("@@@@@@@@@@@@@@@@@ in add", hostname_default, interface_type, interface_name, "in", firewall_name, interface_vif)
                else:
                    pass
                    #print("@@@@@ not 2", interfaces_all_names_dict[ialias], firewall_name )

            fw_changed = True
        elif el.startswith('firewall-ipv4-out'):

            pos = el.split(".")
            
            interface_type = pos[1]
            interface_name = pos[2]
            if len(pos) >= 4:
                interface_vif = pos[3]
                ialias = "{interface_name}.{vif}".format(interface_name=interface_name, vif=interface_vif)
            else:
                ialias = interface_name                

            firewall_name = request.POST[el]
            if firewall_name == "--remove--":
                if 'firewall_out' in interfaces_all_names_dict[ialias]:
                    v = vapi.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "out", interface_vif)
                    #print("@@@@@@@@@@@@@@@@@ out delete", hostname_default, interface_type, interface_name, "out", firewall_name, interface_vif)
                else:
                    #print("@@@@@ not 3", interfaces_all_names_dict[ialias], firewall_name)                    
                    pass
            else:
                if 'firewall_out' not in interfaces_all_names_dict[ialias] or interfaces_all_names_dict[ialias]['firewall_out'] != firewall_name:
                    v = vapi.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name, "out", firewall_name, interface_vif)
                    #print("@@@@@@@@@@@@@@@@@ out add", hostname_default, interface_type, interface_name, "out", firewall_name, interface_vif)
                else:
                    #print("@@@@@ not 4", interfaces_all_names_dict[ialias], firewall_name)
                    pass

            fw_changed = True
            
    if fw_changed == True:
        return redirect('interface:interface-list')



    template = loader.get_template('interface/index.html')
    context = {
        'interfaces':                               interfaces,
        'interfaces_pretty':                        pprint.pformat(interfaces, indent=4, width=120),
        'interfaces_all_names':                     interfaces_all_names,
        'interfaces_all_names_pretty':              pprint.pformat(interfaces_all_names, indent=4, width=120),
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'firewall_all' :                            firewall_all,
        'firewall_names' :                          firewall_names,
        'interface_firewall_in' :                   interface_firewall_in,
        'interface_firewall_out' :                  interface_firewall_out,
        'interface_firewall_in_pretty' :            pprint.pformat(interface_firewall_in, indent=4, width=120),
        'interface_firewall_out_pretty' :           pprint.pformat(interface_firewall_out, indent=4, width=120),
        'username':                                 request.user,   
        'is_superuser' :                            is_superuser,     
    }
    return HttpResponse(template.render(context, request))

@is_authenticated    
def interface_show(request, interface_type, interface_name):
        
    all_instances = perms.instance_getall_by_group(request)
    hostname_default = perms.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)
    
    firewall_all = vyos.get_firewall_all(hostname_default)  
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    interface_detail = vyos.detail_interface(interface_type, interface_name)
    interface_vif = interface_detail['vlan_id']
    interface_name_short = interface_detail['interface_name']
    interface_children = vyos.get_interface_children(hostname_default, interface_name_short)




    template = loader.get_template('interface/show.html')
    context = { 
        'interface_children': interface_children,
        'interface': interface,
        'interface_vif' : interface_vif,
        'instances': all_instances,
        'interface_type' : interface_type,
        'interface_name' : interface_name,
        'hostname_default': hostname_default,
        'firewall_all' : firewall_all,
        'username': request.user,        
        'is_superuser' : is_superuser,               
    }   
    return HttpResponse(template.render(context, request))


@is_authenticated    
def interface_firewall(request, interface_type, interface_name):
        
    all_instances = perms.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    hostname_default = perms.get_hostname_prefered(request)
    
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    
    template = loader.get_template('interface/show.html')
    context = { 
        'interface': interface,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'interface_type' : interface_type,
        'interface_name' : interface_name,        
        'username': request.user,      
        'is_superuser' : is_superuser,  
    }   
    return HttpResponse(template.render(context, request))


@is_authenticated    
def interface_set_firewall(request, interface_type, interface_name):
    hostname_default = perms.get_hostname_prefered(request)
    
    interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    interface_detail = vyos.detail_interface(interface_type, interface_name)
    interface_vif = interface_detail['vlan_id']
    interface_name_short = interface_detail['interface_name']

    actual_firewall_in = None
    if 'firewall' in interface:
        if 'in' in interface['firewall']:
            if 'name' in interface['firewall']['in']:
                actual_firewall_in = interface['firewall']['in']['name']

    actual_firewall_out = None
    if 'firewall' in interface:
        if 'out' in interface['firewall']:
            if 'name' in interface['firewall']['out']:
                actual_firewall_out = interface['firewall']['out']['name']                

    if request.POST.get('firewall-ipv4-in', None) != None and request.POST.get('firewall-ipv4-out', None) != None:
        if request.POST.get('firewall-ipv4-in') == '':
            v = vapi.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name_short, "in", interface_vif)
        elif actual_firewall_in == None or request.POST.get('firewall-ipv4-in') != interface['firewall']['in']['name']:
            v = vapi.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name_short, "in", request.POST.get('firewall-ipv4-in'), interface_vif) 

        if request.POST.get('firewall-ipv4-out') == '':
            v = vapi.delete_interface_firewall_ipv4(hostname_default, interface_type, interface_name_short, "out", interface_vif)
        elif actual_firewall_out == None or request.POST.get('firewall-ipv4-out') != interface['firewall']['out']['name']:
            v = vapi.set_interface_firewall_ipv4(hostname_default, interface_type, interface_name_short, "out", request.POST.get('firewall-ipv4-out'), interface_vif)       
            
    return redirect('interface:interface-show', interface_type=interface_type, interface_name=interface_name)

@is_authenticated    
def interface_set(request, interface_type, interface_name):
    hostname_default = perms.get_hostname_prefered(request)   
    #interface = vyos.get_interface(interface_type, interface_name, hostname=hostname_default)
    interface_detail = vyos.detail_interface(interface_type, interface_name)
    interface_vif = interface_detail['vlan_id']
    interface_name_short = interface_detail['interface_name']   

    address = 'dhcp'
    if request.POST.get('dhcp', None) != "1":
        address = request.POST.get('address', None)
        if address != None:
            address = address.strip()


    mtu = None
    if request.POST.get('mtu','').strip().isdigit():
        mtu = request.POST.get('mtu').strip()
    
    if mtu == None:
        v = vapi.delete_interface_mtu(hostname_default, interface_type, interface_name_short, vif=interface_vif)
    else:
        v = vapi.set_interface_mtu(hostname_default, interface_type, interface_name_short, mtu, vif=interface_vif)

    v = vapi.delete_interface_address(hostname_default, interface_type, interface_name_short, vif=interface_vif)
    v = vapi.set_interface_address(hostname_default, interface_type, interface_name_short, address, vif=interface_vif)

    return redirect('interface:interface-show', interface_type=interface_type, interface_name=interface_name)

@is_authenticated    
def interface_delete(request, interface_type, interface_name, interface_vif=None):
    hostname_default = perms.get_hostname_prefered(request)   
    
    if interface_vif == None:
        v = vapi.delete_interface(hostname_default, interface_type, interface_name)
    else:
        v = vapi.delete_interface(hostname_default, interface_type, interface_name, vif=interface_vif)

    return redirect('interface:interface-list')

@is_authenticated    
def interface_add(request):      
    all_instances = perms.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)
    hostname_default = perms.get_hostname_prefered(request)
    msg = vmsg.msg()

    changed = False

    if request.POST.get('name', None) == None:
        pass
    else:
        interface_name = None
        if validator_letters_numbers(request.POST.get('name', '').strip()):
            interface_name = request.POST.get('name', '').strip()

        interface_address = None
        if validator_ipv4_cidr(request.POST.get('address', '')):
            interface_address = request.POST.get('address', '').strip()

        interface_dhcp = False
        if request.POST.get('dhcp', '0') == '1':
            interface_dhcp = True
            interface_address = 'dhcp'

        interface_mtu = None
        if request.POST.get('mtu','').strip().isdigit():
            interface_mtu = request.POST.get('mtu').strip()
            try:
                interface_mtu = int(interface_mtu)
            except:
                interface_mtu = 1450
            
            if not validators.between(interface_mtu, min=1000, max=9000):
                interface_mtu = 1450
        
        interface_type = 'ethernet'
        interface_types = ['ethernet', 'dummy', 'loopback']
        if request.POST.get('type','ethernet') in interface_types:
            interface_type = request.POST.get('type','ethernet')

        v = vapi.set_interface(hostname_default, interface_type, interface_name)

        if v.success == False:
            msg.add_error("Action: failed to add interface - " + v.reason)
        else:
            msg.add_success("Action: interface added")
            changed = True

        v = vapi.set_interface_mtu(hostname_default, interface_type, interface_name, interface_mtu)
        if v.success == False:
            msg.add_error("Action: failed to set MTU - " + v.reason)
        else:
            msg.add_success("Action: MTU set")

        v = vapi.set_interface_address(hostname_default, interface_type, interface_name, interface_address)
        if v.success == False:
            msg.add_error("Action: failed to set address - " + v.reason)
        else:
            msg.add_success("Action: address set")
        



    template = loader.get_template('interface/add.html')
    context = { 
        'instances':            all_instances,
        'hostname_default':     hostname_default,
        'username':             request.user,      
        'is_superuser':         is_superuser, 
        'msg':                  msg.get_all(),
        'changed':              changed,


    }       

    return HttpResponse(template.render(context, request))


@is_authenticated    
def interface_add_vlan(request, interface_type=None, interface_name=None):      
    all_instances = perms.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)
    hostname_default = perms.get_hostname_prefered(request)
    msg = vmsg.msg()

    changed = False

    if interface_type == None and interface_name == None:
        interface_type = request.POST.get('interface_type')
        interface_name = request.POST.get('interface_name')
        if validator_letters_numbers(interface_type) and validator_letters_numbers(interface_name):
            pass
        else:
            return redirect('interface:interface-list')


    interface_vlan = request.POST.get('vlan', '').strip()
    try:
        interface_vlan = int(interface_vlan)
    except:
        interface_vlan = 0

    if interface_vlan == 0:
        pass
    elif not validators.between(interface_vlan, min=1, max=4095):
        msg.add_error("VLAN need to be between 1 and 4095")
    else:
        interface_address = None
        if validator_ipv4_cidr(request.POST.get('address', '')):
            interface_address = request.POST.get('address', '').strip()

        interface_dhcp = False
        if request.POST.get('dhcp', '0') == '1':
            interface_dhcp = True
            interface_address = 'dhcp'

        interface_mtu = 0
        if request.POST.get('mtu','').strip().isdigit():
            interface_mtu = request.POST.get('mtu').strip()
            try:
                interface_mtu = int(interface_mtu)
            except:
                interface_mtu = 1450
            
        if not validators.between(interface_mtu, min=1000, max=9000):
            interface_mtu = 1450
    
        
        interface_mtu = str(interface_mtu)
        interface_vlan = str(interface_vlan)

        interface_type = 'ethernet'

        v = vapi.set_interface(hostname_default, interface_type, interface_name, vif=interface_vlan)

        if v.success == False:
            msg.add_error("Action: failed to add interface - " + v.reason)
        else:
            msg.add_success("Action: interface added")
            changed = True

        v = vapi.set_interface_mtu(hostname_default, interface_type, interface_name, interface_mtu, vif=interface_vlan)
        if v.success == False:
            msg.add_error("Action: failed to set MTU - " + v.reason)
        else:
            msg.add_success("Action: MTU set")

        v = vapi.set_interface_address(hostname_default, interface_type, interface_name, interface_address, vif=interface_vlan)
        if v.success == False:
            msg.add_error("Action: failed to set address - " + v.reason)
        else:
            msg.add_success("Action: address set")
        



    template = loader.get_template('interface/add_vlan.html')
    context = { 
        'instances':            all_instances,
        'hostname_default':     hostname_default,
        'username':             request.user,      
        'is_superuser':         is_superuser, 
        'msg':                  msg.get_all(),
        'changed':              changed,

        'interface_name':       interface_name,
        'interface_type':       interface_type,


    }       

    return HttpResponse(template.render(context, request))
