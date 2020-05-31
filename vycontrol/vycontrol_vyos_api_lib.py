import requests
import json
import pprint
import sys
import logging
#logger = logging.getLogger(__name__)


from config.models import Instance
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

import perms
from vycontrol_messages import log

class vyapi:
    error =     None
    success =   None
    result =    None
    data =      None
    reason =    None
    def __init__(self, result, data = None, reason=None):

        if result == True:
            self.success = True
        else:
            self.error = True
        self.result = result
        self.data = data
        self.reason = reason

log("api " + " !!!!!!!!!!!!!! START NEW WEB PROCESS", end=False)

API_LIST = {}
API_LIST["get"] = {}
API_LIST["get"]["description"]              = 'Show config'
API_LIST["get"]["path"]                     = 'retrieve'
API_LIST["get"]["op"] = {}
API_LIST["get"]["op"]["showConfig"]         = 'path'

API_LIST["post"] = {}
API_LIST["post"]["description"]              = 'Configuration mode requests'
API_LIST["post"]["path"]                     = "configure"
API_LIST["post"]["op"] = {}
API_LIST["post"]["op"]["set"]                = 'path'
API_LIST["post"]["op"]["delete"]             = 'path'
API_LIST["post"]["op"]["comment"]            = 'path'

API_LIST["conf"] = {}
API_LIST["conf"]["description"]              = 'Configuration management requests'
API_LIST["conf"]["path"]                     = 'config-file'
API_LIST["conf"]["op"] = {}
API_LIST["conf"]["op"]["save"]               = 'file'
API_LIST["conf"]["op"]["load"]               = 'file'

API_LIST["op-generate"] = {}
API_LIST["op-generate"]["description"]       = 'Operational mode commands - generate'
API_LIST["op-generate"]["path"]              = 'generate'
API_LIST["op-generate"]["op"] = {}
API_LIST["op-generate"]["op"]["generate"]    = 'path'

API_LIST["op-show"] = {}
API_LIST["op-show"]["description"]           = 'Operational mode commands - show'
API_LIST["op-show"]["path"]                  = 'show'
API_LIST["op-show"]["op"] = {}
API_LIST["op-show"]["op"]["show"]            = 'path'


def get_key(hostname):
    # permcheck
    instance = Instance.objects.get(hostname=hostname)
    return instance.key

def get_api_data(hostname, api, op, cmd):
    instance = Instance.objects.get(hostname=hostname)

    if instance.https == True:
        protocol = "https"
    else:
        protocol = "http"

    if instance.port == None:
        instance.port = 443

    api_exists = False
    if (    api in API_LIST 
        and 'op' in API_LIST[api]
        and op in API_LIST[api]['op']
    ):
        api_exists =        True
        api_op =            op
        api_path =          API_LIST[api]['path']
        api_subcommand =    API_LIST[api]['op'][op]
    else:
        return False

    if api_exists == False:
        return False
    else:
        #log("api_path ", api_path)
        #log("protocol ", protocol)
        #log("instance.hostname ", instance.hostname)
        #log("instance.port ", instance.port)
        api_url = protocol + "://" + instance.hostname + ":" + str(instance.port) + "/" + api_path
        api_data = {
            'api_url':          api_url,
            'api_op':           api_op,
            'api_subcommand':   api_subcommand
        }
        log("api call", api_data)
        return api_data


def api(hostname, api, op, cmd, description = ""):
    api_data = get_api_data(hostname=hostname, api=api, op=op, cmd=cmd)

    if api_data == False:
        v = vyapi(result = False)
        return v

    cmd = {
        "op":                           api_data['api_op'],
        api_data['api_subcommand'] :    cmd
    }
     
    post = {'key': get_key(hostname), 'data': json.dumps(cmd)}
    log("api " +  api_data['api_subcommand'], post)


    post = {
        'key':      get_key(hostname),
        'data':     json.dumps(cmd)
    }

    try:
        resp = requests.post(api_data['api_url'], verify=False, data=post, timeout=10)
    except requests.exceptions.ConnectionError:
        try:
            status_code = resp.status_code
        except UnboundLocalError:
            status_code = 0
        
        v = vyapi(result = False, reason= {
            'exception'     : 'requests.exceptions.ConnectionError',
            'respcode'      : status_code
        })
        log("failed to post url", api_data['api_url'])

        return v



    try:
        respjson = resp.json()
    except json.JSONDecodeError:
        respjson = {'success': False, 'error': None, 'data': None}

    #log("api raw", respjson)


    v = vyapi(
        result =    respjson['success'],
        reason =    respjson['error'],
        data =      respjson['data']
    )   

    log("api resp", [v.result, v.reason, v.data])




    log_vars = {
        'api_url':      api_data['api_url'],
        'api_op':       api_data['api_op'],
        'api_cmd':      cmd,
        'resp_obj':     resp,
        'resp_code':    resp.status_code,
        'resp_result':  v.result,
        'resp_reason':  v.reason,
        'resp_data':    v.data
    }

    log("api " + description, log_vars)

    return v

    


