import requests
import json
import pprint
import sys

from config.models import Instance
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


import perms

def repvar(s):
    return s.replace("-", "_")

def get_url(hostname):
    # permcheck
    try:
        instance = Instance.objects.get(hostname=hostname)
    except Instance.DoesNotExist:
        return ''

    if instance.https == True:
        protocol = "https"
    else:
        protocol = "http"

    if (instance.port == None):
        instance.port = 443

    url = protocol + "://" + instance.hostname + ":" + str(instance.port)

    return url

def get_url_manage(hostname):
    url = get_url(hostname) + '/config-file'
    return url

def get_url_configure(hostname):
    url = get_url(hostname) + '/configure'
    return url

def get_url_show(hostname):
    url = get_url(hostname) + '/show'
    return url

def get_url_retrieve(hostname):
    url = get_url(hostname) + '/retrieve'        
    return url

def get_key(hostname):
    try:
        instance = Instance.objects.get(hostname=hostname)
    except Instance.DoesNotExist:
        return None

    return instance.key

def api(type, hostname, cmd):
    if type == "retrieve":
        url = get_url_retrieve(hostname)
    elif type == "manage":
        url = get_url_manage(hostname)
    elif type == "configure":
        url = get_url_configure(hostname)
    elif type == "show":
        url = get_url_show(hostname)        
    else:
        return False

    pprint.pprint(cmd)
    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)   

    try:
        resp = requests.post(url, verify=False, data=post, timeout=10)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())

    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return False
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']

def api_get(hostname, cmd):
    return api('retrieve', hostname, cmd)

def api_show(hostname, cmd):
    return api('show', hostname, cmd)    

def api_set(hostname, cmd):
    return api('configure', hostname, cmd)    
    
def conntry(hostname): 
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    
    print(get_url_retrieve(hostname))

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=10)
    except requests.exceptions.ConnectionError:
        return False
    
    print(resp.status_code)

    if (resp.status_code == 200):
        return True
    
    pprint.pprint(resp)
    pprint.pprint(resp.json())

    return False


def get_firewall_all(hostname):
    cmd = {"op": "showConfig", "path": ["firewall"]}
    firewall_list = api_get(hostname, cmd)

    nfirewall_list = {}

    for f in firewall_list:
        s = repvar(f)
        nfirewall_list[s] = firewall_list[f]
        nfirewall_list[f] = firewall_list[f]        

    return nfirewall_list

  

def get_interfaces(hostname):
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    result1 = api_get(hostname, cmd)
    return result1

def detail_interface(interface_type, interface_name):
    vlan = False
    vlan_id = None

    if interface_type == "ethernet":
        isplit = interface_name.split(".")
        if len(isplit) == 2:
            vlan = True
            vlan_id = isplit[1]
            interface_name = isplit[0]

    return {
        "interface_name":   interface_name,
        "vlan":             vlan,
        "vlan_id":          vlan_id,
        "interface_type":   interface_type
    }

def get_interfaces_all_names(hostname):
    interfaces = get_interfaces(hostname)

    all_names = []

    for itype in interfaces:
        for iname in interfaces[itype]:
            interface_info = detail_interface(itype, iname)

            all_names.append({
                'interface_name':           iname,
                'type':                     itype,
                'interface_short':          interface_info['interface_name']
            })
            
            if 'vif' in interfaces[itype][iname]:
                for vif in interfaces[itype][iname]['vif']:

                    all_names.append({
                        'interface_name':   iname,
                        'type':             itype,
                        'vif':              vif,
                        'interface_short':  interface_info['interface_name']
                    })                    
    
    return all_names


def get_interface(interface_type, interface_name, hostname):
    inteface_detail = detail_interface(interface_type, interface_name)

        
    if inteface_detail['vlan'] == True:
        cmd = {"op": "showConfig", "path": ["interfaces", inteface_detail['interface_type'], inteface_detail['interface_name'], "vif", inteface_detail['vlan_id']]}
    else:
        cmd = {"op": "showConfig", "path": ["interfaces", inteface_detail['interface_type'], inteface_detail['interface_name']]}

    result1 = api_get(hostname, cmd)
    return result1
  
def get_firewall(hostname, name):
    cmd = {"op": "showConfig", "path": ["firewall", "name", name]}

    result1 = api_get(hostname, cmd)
    return result1

def get_firewall_rule(hostname, name, rulenumber):
    cmd = {"op": "showConfig", "path": ["firewall", "name", name, "rule", rulenumber]}

    result1 = api_get(hostname, cmd)
    return result1

def set_config(hostname, cmd):
    #cmd = {"op": "set", "path": ["interface", interface_type, interface_name, "firewall", direction, "name", firewall_name]}
    result1 = api_set(hostname, cmd)
    return result1

def insert_firewall_rules(hostname, cmd):
    pprint.pprint(cmd)
    result1 = api_set(hostname, cmd)
    return result1

def get_route_static(hostname):
    cmd = {"op": "showConfig", "path": ["protocols","static","route"]}

    result1 = api_get(hostname, cmd)
    return result1


def set_firewall_syncookies_enable(hostname):
    cmd = {"op": "set", "path": ["firewall","syn-cookies",'enable']}

    result1 = api_set(hostname, cmd)
    return result1  

def set_firewall_syncookies_disable(hostname):
    cmd = {"op": "set", "path": ["firewall","syn-cookies",'disable']}

    result1 = api_set(hostname, cmd)
    return result1  


def set_firewall_allping_enable(hostname):
    cmd = {"op": "set", "path": ["firewall","all-ping",'enable']}

    result1 = api_set(hostname, cmd)
    return result1  

def set_firewall_allping_disable(hostname):
    cmd = {"op": "set", "path": ["firewall","all-ping",'disable']}

    result1 = api_set(hostname, cmd)
    return result1  

def get_firewall_portgroup(hostname):
    cmd = {"op": "showConfig", "path": ["firewall","group","port-group"]}
    result1 = api_get(hostname, cmd)
    return result1

def set_firewall_portgroup_del(hostname, group_name):
    cmd = {"op": "delete", "path": ["firewall","group",'port-group', group_name]}
    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_portgroup_description(hostname, group_name, description):
    cmd = {"op": "set", "path": ["firewall","group",'port-group', group_name, "description", description]}
    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_portgroup_add(hostname, group_name, port):
    cmd = {"op": "set", "path": ["firewall","group",'port-group', group_name, "port", port]}

    result1 = api_set(hostname, cmd)
    return result1    

def set_firewall_portgroup_delete_port(hostname, group_name, port):
    cmd = {"op": "delete", "path": ["firewall","group",'port-group', group_name, "port", port]}

    result1 = api_set(hostname, cmd)
    return result1         

def get_firewall_addressgroup(hostname):
    cmd = {"op": "showConfig", "path": ["firewall","group","address-group"]}
    result1 = api_get(hostname, cmd)
    return result1    

def get_firewall_networkgroup(hostname):
    cmd = {"op": "showConfig", "path": ["firewall","group","network-group"]}
    result1 = api_get(hostname, cmd)
    return result1

def get_firewall_addressgroup_one(hostname, group_name):
    cmd = {"op": "showConfig", "path": ["firewall","group","address-group", group_name]}
    result1 = api_get(hostname, cmd)
    return result1

def get_firewall_networkgroup_one(hostname, group_name):
    cmd = {"op": "showConfig", "path": ["firewall","group","network-group", group_name]}
    result1 = api_get(hostname, cmd)
    return result1


def set_firewall_networkgroup_description(hostname, group_name, description):
    cmd = {"op": "set", "path": ["firewall","group",'network-group', group_name, "description", description]}
    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_addressgroup_description(hostname, group_name, description):
    cmd = {"op": "set", "path": ["firewall","group",'address-group', group_name, "description", description]}
    result1 = api_set(hostname, cmd)
    return result1     



def set_firewall_addressgroup_add(hostname, group_name, address):
    cmd = {"op": "set", "path": ["firewall","group",'address-group', group_name, "address", address]}

    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_addressgroup_del(hostname, group_name):
    cmd = {"op": "delete", "path": ["firewall","group",'address-group', group_name]}
    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_networkgroup_del(hostname, group_name):
    cmd = {"op": "delete", "path": ["firewall","group",'network-group', group_name]}
    result1 = api_set(hostname, cmd)
    return result1 




def set_firewall_addressgroup_rangeadd(hostname, group_name, address_start, address_end):
    address = str(address_start) + "-" + str(address_end)
    cmd = {"op": "set", "path": ["firewall","group",'address-group', group_name, "address", address]}

    result1 = api_set(hostname, cmd)
    return result1     

def set_firewall_addressgroup_description(hostname, group_name, description):
    cmd = {"op": "set", "path": ["firewall","group",'address-group', group_name, "description", description]}

    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_networkgroup_add(hostname, group_name, network):
    cmd = {"op": "set", "path": ["firewall","group",'network-group', group_name, "network", network]}

    result1 = api_set(hostname, cmd)
    return result1 

def set_firewall_networkgroup_description(hostname, group_name, description):
    cmd = {"op": "set", "path": ["firewall","group",'network-group', group_name, "description", description]}

    result1 = api_set(hostname, cmd)
    return result1 




def delete_route_static(hostname, subnet, nexthop):
    #cmd = {"op": "delete", "path": ["protocols","static","route", subnet, "next-hop", nexthop]}
    cmd = {"op": "delete", "path": ["protocols","static","route", subnet]}

    result1 = api_set(hostname, cmd)
    return result1  

def delete_route_rule(hostname, firewall_name, rule_name):
    cmd = {"op": "delete", "path": ["firewall", "name", firewall_name, "rule", rule_name]}

    result1 = api_set(hostname, cmd)
    return result1  


def delete_firewall(hostname, name):
    cmd = {"op": "delete", "path": ["firewall","name", name]}

    result1 = api_set(hostname, cmd)
    return result1            


def ip_route(hostname):
    cmd = {"op": "show", "path": ["ip","route"]}

    result1 = api_show(hostname, cmd)
    return result1        


def get_interface_children(hostname, interface_name):
    interfaces_all_names = get_interfaces_all_names(hostname)

    interface_children = []

    for iname in interfaces_all_names:
        if interface_name == iname['interface_name']:
            if 'vif' in iname:
                interface_children.append({'name': interface_name, 'vif': iname['vif'], 'type': iname['type']})

    return interface_children        