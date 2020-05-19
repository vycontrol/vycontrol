import requests
import json
import pprint
import sys
import logging

import vycontrol_vyos_api_lib as vapilib
import perms



def get_firewall_rulenumber(hostname, firewall, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "name", firewall, "rule", rulenumber],
        description = "get_firewall_rulenumber",
    )
    return v


def get_firewall_group(hostname):
    v = vapilib.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "group"],
        description = "get_firewall_group",
    )
    return v


def set_firewall_rule_action(hostname, firewall_name, rulenumber, action):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "action", action],
        description = "set rule action",
    )
    return v

def set_firewall_rule_disabled(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "disable"],
        description = "disable rule",
    )
    return v    

def set_firewall_rule_enabled(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "disable"],
        description = "enable rule",
    )
    return v    
