import requests
import json
import pprint
import sys

#curl -k -X POST -F data='{"op": "set", "path": ["interfaces", "dummy", "dum1", "address"], "value": "203.0.113.76/32"}' -F key=a6ffb742a8a631a65b07ab2026258629da2632fd https://179.127.12.142:44302/configure

sys.path.append('/var/secrets')
import local




 
SERVER_URL_MANAGE = local.SERVER_URL + 'config-file'
SERVER_URL_CONFIG = local.SERVER_URL + 'configure'
SERVER_URL_RETRIE = local.SERVER_URL + 'retrieve'

#data='{"op": "showConfig", "path": ["interfaces", "dummy"]}


def getall():
    #cmd = {"op": "save", "file": "/config/config.boot"}
    cmd = {"op": "showConfig", "path": ["interfaces", "dummy"]}

    print(json.dumps(cmd))
    post = {'key': local.SERVER_KEY, 'data': json.dumps(cmd)}
    print(post)


    # curl -X POST -F data='{"op": "showConfig", "path": ["interfaces", "dummy"]}' -F key=qwerty http://127.0.0.1:8080/retrieve
    # {"success": true, "data": " /* So very dummy */\n dummy dum0 {\n     address 192.168.168.1/32\n     address 192.168.168.2/32\n     /* That is a description */\n     description \"Test interface\"\n }\n dummy dum1 {\n     address 203.0.113.76/32\n     address 203.0.113.79/32\n }\n", "error": null}

    resp = requests.post(SERVER_URL_RETRIE, verify=False, data=post)
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


def get_interfaces():
    cmd = {"op": "showConfig", "path": ["interfaces"]}

    print(json.dumps(cmd))
    post = {'key': local.SERVER_KEY, 'data': json.dumps(cmd)}
    print(post)


    # curl -X POST -F data='{"op": "showConfig", "path": ["interfaces", "dummy"]}' -F key=qwerty http://127.0.0.1:8080/retrieve
    # {"success": true, "data": " /* So very dummy */\n dummy dum0 {\n     address 192.168.168.1/32\n     address 192.168.168.2/32\n     /* That is a description */\n     description \"Test interface\"\n }\n dummy dum1 {\n     address 203.0.113.76/32\n     address 203.0.113.79/32\n }\n", "error": null}

    resp = requests.post(SERVER_URL_RETRIE, verify=False, data=post)
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

def get_interface(interface_type, interface_name):
    cmd = {"op": "showConfig", "path": ["interfaces", interface_type, interface_name]}

    print(json.dumps(cmd))
    post = {'key': local.SERVER_KEY, 'data': json.dumps(cmd)}
    print(post)


    # curl -X POST -F data='{"op": "showConfig", "path": ["interfaces", "dummy"]}' -F key=qwerty http://127.0.0.1:8080/retrieve
    # {"success": true, "data": " /* So very dummy */\n dummy dum0 {\n     address 192.168.168.1/32\n     address 192.168.168.2/32\n     /* That is a description */\n     description \"Test interface\"\n }\n dummy dum1 {\n     address 203.0.113.76/32\n     address 203.0.113.79/32\n }\n", "error": null}

    resp = requests.post(SERVER_URL_RETRIE, verify=False, data=post)
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

