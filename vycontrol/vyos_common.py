import requests
import json
import pprint
import sys
import logging
import vyos2

import perms



def get_firewall_rulenumber(hostname, firewall, rulenumber):
    v = vyos2.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "name", firewall, "rule", rulenumber],
        description = "get_firewall_rulenumber",
    )
    return v


def get_firewall_networkgroup(hostname):
    v = vyos2.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "group", "network"],
        description = "get_firewall_networkgroup",
    )
    return v

