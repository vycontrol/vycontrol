import requests
import json
import pprint
import sys

#curl -k -X POST -F data='{"op": "set", "path": ["interfaces", "dummy", "dum1", "address"], "value": "203.0.113.76/32"}' -F key=a6ffb742a8a631a65b07ab2026258629da2632fd https://179.127.12.142:44302/configure

sys.path.append('/var/secrets')

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
    
def instance_getall():
    instances = Instance.objects.all()
    return instances


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




def getall(hostname="179.127.12.142"):
    #cmd = {"op": "save", "file": "/config/config.boot"}
    cmd = {"op": "showConfig", "path": ["interfaces", "dummy"]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False


    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    return resp


def get_interfaces(hostname="179.127.12.142"):
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']

def get_interface(interface_type, interface_name, hostname):
    cmd = {"op": "showConfig", "path": ["interfaces", interface_type, interface_name]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']



def get_firewall_all(hostname):
    cmd = {"op": "showConfig", "path": ["firewall"]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)

    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']



def get_firewall(hostname, name):
    cmd = {"op": "showConfig", "path": ["firewall", "name", name]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)


    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']



def get_firewall_rule(hostname, name, rulenumber):
    cmd = {"op": "showConfig", "path": ["firewall", "name", name, "rule", rulenumber]}

    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)


    try:
        resp = requests.post(get_url_retrieve(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']



def set_config(hostname, cmd):
    print(json.dumps(cmd))
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    print(post)


    try:
        resp = requests.post(get_url_configure(hostname), verify=False, data=post, timeout=15)
    except requests.exceptions.ConnectionError:
        return False

    print(resp.status_code)
    pprint.pprint(resp)

    pprint.pprint(resp.json())


    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
        return "erro"
    #for todo_item in resp.json():
        #print('{} {}'.format(todo_item['id'], todo_item['summary']))

    result1 = resp.json()
    print(result1['data'])
    #result2 = json.loads(result1['data'])
    pprint.pprint(result1)

    return result1['data']


def insert_firewall_rules(hostname, firewall_name):
    cmd = {"op": "set", "path": ["firewall", firewall_name, "rule", request.POST['rulenumber'], "action", request.POST['action']]}
    result1 = set_config(hostname, cmd)



#curl -k -X POST -F data='{"op": "set", "path": ["interfaces", "dummy", "dum1", "address"], "value": "203.0.113.76/32"}' -F key=a6ffb742a8a631a65b07ab2026258629da2632fd https://179.127.12.142:44302/configure

