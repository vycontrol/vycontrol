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

def set_firewall_rule_description(hostname, firewall_name, rulenumber, description):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "description", description],
        description = "set rule description",
    )
    return v

def set_firewall_rule_protocol(hostname, firewall_name, rulenumber, protocol_criteria_txt):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "protocol", protocol_criteria_txt],
        description = "set rule protocol",
    ) 
    return v

def set_firewall_rule_protocol_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "protocol"],
        description = "delete rule protocol",
    ) 
    return v

def set_firewall_rule_destination_ports(hostname, firewall_name, rulenumber, ports):
    ports_text = ','.join(ports)

    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "port", ports_text],
        description = "set destination ports",
    ) 
    return v

def set_firewall_rule_source_ports(hostname, firewall_name, rulenumber, ports):
    ports_text = ','.join(ports)

    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "port", ports_text],
        description = "set source ports",
    ) 
    return v


def set_firewall_rule_destination_ports_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "port"],
        description = "delete destination port",
    ) 
    return v


def set_firewall_rule_source_ports_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "port"],
        description = "delete source port",
    ) 
    return v    


def set_firewall_rule_tcpflags(hostname, firewall_name, rulenumber, tcpflags):
    if len(tcpflags) > 0:
        tcpflags_txt = ",".join(tcpflags)
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "tcp", "flags", tcpflags_txt],
            description = "set tcpflags",
        )
    return v

def set_firewall_rule_tcpflags_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "tcp", "flags"],
        description = "delete tcpflags",
    )
    return v    


def set_firewall_rule_source_address(hostname, firewall_name, rulenumber, address):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "address", address],
        description = "set saddress",
    )
    return v

def set_firewall_rule_destination_address(hostname, firewall_name, rulenumber, address):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "address", address],
        description = "set daddress",
    )
    return v

def set_firewall_rule_source_address_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "address"],
        description = "set saddress",
    )
    return v

def set_firewall_rule_destination_address_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "address"],
        description = "set daddress",
    )
    return v    

def set_firewall_rule_source_addressgroup(hostname, firewall_name, rulenumber, saddressgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "address-group", saddressgroup],
        description = "set saddressgroup",
    )
    return v  

def set_firewall_rule_destination_addressgroup(hostname, firewall_name, rulenumber, daddressgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "address-group", daddressgroup],
        description = "set daddressgroup",
    )
    return v 

def set_firewall_rule_source_addressgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "address-group"],
        description = "delete saddressgroup",
    )
    return v  

def set_firewall_rule_destination_addressgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "address-group"],
        description = "delete daddressgroup",
    )
    return v     


def set_firewall_rule_source_networkgroup(hostname, firewall_name, rulenumber, snetworkgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "network-group", snetworkgroup],
        description = "set snetworkgroup",
    )
    return v  

def set_firewall_rule_destination_networkgroup(hostname, firewall_name, rulenumber, dnetworkgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "network-group", dnetworkgroup],
        description = "set dnetworkgroup",
    )
    return v 

def set_firewall_rule_source_networkgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "network-group"],
        description = "delete snetworkgroup",
    )
    return v  

def set_firewall_rule_destination_networkgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "network-group"],
        description = "delete dnetworkgroup",
    )
    return v         

def set_firewall_rule_source_portgroup(hostname, firewall_name, rulenumber, sportgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "port-group", sportgroup],
        description = "set sportgroup",
    )
    return v  

def set_firewall_rule_destination_portgroup(hostname, firewall_name, rulenumber, dportgroup):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "port-group", dportgroup],
        description = "set dportgroup",
    )
    return v 

def set_firewall_rule_source_portgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "port-group"],
        description = "delete sportgroup",
    )
    return v  

def set_firewall_rule_destination_portgroup_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "port-group"],
        description = "delete dportgroup",
    )
    return v             

def set_firewall_rule_source_mac(hostname, firewall_name, rulenumber, smac_txt):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "mac-address", smac_txt],
        description = "set source mac",
    )
    return v

def set_firewall_rule_source_mac_delete(hostname, firewall_name, rulenumber):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "mac-address"],
        description = "delete dportgroup",
    )
    return v

def set_firewall_rule_packetstate(hostname, firewall_name, rulenumber, packetstate):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "state", packetstate, "enable"],
        description = "set packetstate",
    )
    return v

def set_firewall_rule_packetstate_delete(hostname, firewall_name, rulenumber, packetstate):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "state", packetstate],
        description = "delete packetstate",
    )
    return v


def set_route_static(hostname, subnet, nexthop):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["protocols", "static", "route", subnet, "next-hop", nexthop],
        description = "set_route_static",
    )
    return v


def set_firewall_zone_localzone(hostname, zonename):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["zone-policy", "zone", zonename, "local-zone"],
        description = "set_firewall_zone_localzone",
    )
    return v    


def set_firewall_zone_description(hostname, zonename, description):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["zone-policy", "zone", zonename, "description", description],
        description = "set_firewall_zone_description",
    )
    return v    

def set_firewall_zone_defaultaction(hostname, zonename, defaultaction):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["zone-policy", "zone", zonename, "default-action", defaultaction],
        description = "set_firewall_zone_defaultaction",
    )
    return v  

def set_firewall_zone_interface(hostname, zonename, interface):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["zone-policy", "zone", zonename, "interface", interface],
        description = "set_firewall_zone_interface",
    )
    return v    

def delete_firewall_zone_interface(hostname, zonename, interface):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["zone-policy", "zone", zonename, "interface", interface],
        description = "delete_firewall_zone_interface",
    )
    return v   

def delete_firewall_zone(hostname, zonename):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["zone-policy", "zone", zonename],
        description = "delete_firewall_zone",
    )
    return v       


def get_firewall_zones(hostname):
    v = vapilib.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["zone-policy"],
        description = "get_firewall_zones",
    )
    return v

def get_firewall_zone(hostname, zone):
    v = vapilib.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["zone-policy", "zone", zone],
        description = "get_firewall_zone",
    )
    return v


def set_interface_firewall_ipv4(hostname, interface_type, interface_name, direction, firewall_name, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "firewall", direction, "name", firewall_name],
            description = "set_interface_firewall_ipv4",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "firewall", direction, "name", firewall_name],
            description = "set_interface_firewall_ipv4",
        )
    return v    

def delete_interface_firewall_ipv4(hostname, interface_type, interface_name, direction, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "firewall", direction],
            description = "delete_interface_firewall_ipv4",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "firewall", direction],
            description = "delete_interface_firewall_ipv4",
        )
    return v    





def set_interface_firewall_zone_addrule(hostname, dstzone, srczone, firewall):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["zone-policy", "zone", dstzone, "from", srczone, "firewall", "name", firewall],
        description = "set_interface_firewall_zone_addrule",
    )
    return v  


def delete_interface_firewall_zone_rule(hostname, dstzone, srczone):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["zone-policy", "zone", dstzone, "from", srczone],
        description = "delete_interface_firewall_zone_rule",
    )
    return v  


def delete_interface_firewall_zone_rule_firewall(hostname, dstzone, srczone, firewall):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["zone-policy", "zone", dstzone, "from", srczone, "firewall", "name", firewall],
        description = "delete_interface_firewall_zone_rule",
    )
    return v  

def get_ntp(hostname):
    v = vapilib.api (
        hostname=   hostname,
        api =       "get",
        op =        "showConfig",
        cmd =       ["system","ntp"],
        description = "get_ntp",
    )
    return v

def delete_ntp(hostname, server):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "delete",
        cmd =       ["system","ntp","server",server],
        description = "delete_ntp",
    )
    return v
    
def set_ntp(hostname, server):
    v = vapilib.api (
        hostname=   hostname,
        api =       "post",
        op =        "set",
        cmd =       ["system","ntp","server",server],
        description = "set_ntp",
    )
    return v  

def set_interface_address(hostname, interface_type, interface_name, address, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "address", address],
            description = "set_interface_dhcp",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "address", address],
            description = "set_interface_dhcp",
        )
    return v    


def delete_interface_address(hostname, interface_type, interface_name, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "address"],
            description = "delete_interface_address",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "address"],
            description = "delete_interface_address",
        )
    return v      



def set_interface_mtu(hostname, interface_type, interface_name, mtu, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "mtu", mtu],
            description = "set_interface_mtu",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "mtu", mtu],
            description = "set_interface_mtu",
        )
    return v    


def delete_interface_mtu(hostname, interface_type, interface_name, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "mtu"],
            description = "delete_interface_mtu",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif, "mtu"],
            description = "delete_interface_mtu",
        )
    return v        


def delete_interface(hostname, interface_type, interface_name, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name],
            description = "delete_interface",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "delete",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif],
            description = "delete_interface",
        )
    return v
    
def set_interface(hostname, interface_type, interface_name, vif=None):
    if vif == None:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name],
            description = "set_interface_dhcp",
        )
    else:
        v = vapilib.api (
            hostname=   hostname,
            api =       "post",
            op =        "set",
            cmd =       ["interfaces", interface_type, interface_name, "vif", vif],
            description = "set_interface_dhcp",
        )
    return v   