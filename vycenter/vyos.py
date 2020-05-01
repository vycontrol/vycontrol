import requests
import json
import pprint
import sys

from config.models import Instance

def get_url(hostname):
    # permcheck
    instance = Instance.objects.get(hostname=hostname)
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

def get_url_retrieve(hostname):
    url = get_url(hostname) + '/retrieve'        
    return url

def get_key(hostname):
    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    return instance.key

def api(type, hostname, cmd):
    if type == "retrieve":
        url = get_url_retrieve(hostname)
    elif type == "manage":
        url = get_url_manage(hostname)
    elif type == "configure":
        url = get_url_configure(hostname)
    else:
        return False

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)   

    try:
        resp = requests.post(url, verify=False, data=post, timeout=5)
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

def api_set(hostname, cmd):
    return api('configure', hostname, cmd)    

def get_hostname_prefered(request):
    hostname = None

    if request.session.get('hostname', None) != None:
        hostname = request.session.get('hostname', None)
        

    if hostname == None:
        try:
            instance = Instance.objects.get(main=True)
        except Instance.DoesNotExist:
            return None

        hostname = instance.hostname

    return hostname 
    
def conntry(hostname): 
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    
    print(get_url_retrieve(hostname))

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False
    
    print(resp.status_code)

    if (resp.status_code == 200):
        return True
    
    pprint.pprint(resp)
    pprint.pprint(resp.json())

    return False

def instance_getall():
    instances = Instance.objects.all()
    return instances

def get_firewall_all(hostname):
    cmd = {"op": "showConfig", "path": ["firewall"]}
    firewall_list = api_get(hostname, cmd)
    return firewall_list

def set_interface_firewall_ipv4(hostname, interface_type, interface_name, direction, firewall_name):
    cmd = {"op": "set", "path": ["interface", interface_type, interface_name, "firewall", direction, "name", firewall_name]}
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}

    success = api_set(hostname, cmd)
    return success

def get_interfaces(hostname):
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    result1 = api_get(hostname, cmd)
    return result1

def get_interface(interface_type, interface_name, hostname):
    cmd = {"op": "showConfig", "path": ["interfaces", interface_type, interface_name]}

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