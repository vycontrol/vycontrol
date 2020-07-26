from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.http import QueryDict


import vyos
import vycontrol_vyos_api_lib as vapilib
import vycontrol_vyos_api as vapi
import vycontrol_messages as vmsg

from slugify import slugify
from performance import timer
from perms import is_authenticated
import perms
import network
import json
import pprint
import types


from filters.vycontrol_filters import get_item
from filters.vycontrol_filters import get_item_port
from filters.vycontrol_filters import get_item_network



@is_authenticated
def index(request):

    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall_by_group(request)
    hostname_default = vyos.get_hostname_prefered(request)


    """firewall2 = vapilib.api(
        hostname =      hostname_default,
        api =           'get',
        op =            'showConfig',
        cmd =           {"op": "showConfig", "path": ["firewall"]},
        description =   "get all firewall",
    )"""


    is_superuser = perms.get_is_superuser(request.user)



    firewall_all = vyos.get_firewall_all(hostname_default)
    if firewall_all == False or firewall_all['name'] == False:
        return redirect('firewall:firewall-create')

    for xitem in firewall_all['name']:
        if 'default-action' in firewall_all['name'][xitem]:
            firewall_all['name'][xitem]['default_action'] = firewall_all['name'][xitem]['default-action']
            del firewall_all['name'][xitem]['default-action']

    template = loader.get_template('firewall/list.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'firewall_all':                             firewall_all,
        'username':                                 request.user,
        'is_superuser' :                            is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def create(request):
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    if 'name' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", request.POST['name']]}
        result1 = vyos.set_config(hostname_default, cmd)
        print(result1)

        if 'description' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "description", request.POST['description']]}
            result2 = vyos.set_config(hostname_default, cmd)
            print(result2)

        if 'action' in request.POST:
            cmd = {"op": "set", "path": ["firewall", "name", request.POST['name'], "default-action", request.POST['action']]}
            result3 = vyos.set_config(hostname_default, cmd)
            print(result3)

        return redirect('firewall:firewall-list')

    template = loader.get_template('firewall/create.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_removerule(request, firewall_name, firewall_rulenumber):
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    firewall_rule = vyos.get_firewall_rule(hostname_default, firewall_name, firewall_rulenumber)

    if firewall_rule and firewall:
        vyos.delete_route_rule(hostname_default, firewall_name, firewall_rulenumber)

    return redirect('firewall:show', firewall_name)

def changerule(request, firewall_name, mode, rulenumber=None):
    msg = vmsg.msg()

    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    # get all firewall groups
    firewall_group = {}
    changed = False
    rulenumber_valid = False
    ruledata = {}

    # netservices /etc/services parser
    netservices = network.get_services()

    # firewall groups         
    firewall_group['network-group'] = {}
    firewall_group['address-group'] = {}
    firewall_group['port-group'] = {}
    firewall_group_raw = vapi.get_firewall_group(hostname_default)
    if firewall_group_raw.success:
        if 'network-group' in firewall_group_raw.data:
            firewall_group['network-group'] = firewall_group_raw.data['network-group']

        if 'address-group' in firewall_group_raw.data:
            firewall_group['address-group'] = firewall_group_raw.data['address-group']

        if 'port-group' in firewall_group_raw.data:
            firewall_group['port-group'] = firewall_group_raw.data['port-group']
    
    # edit rule without valid rulenumber
    if mode == "editrule":
        if rulenumber == None:
            msg.add_error("Rule number empty")
        else:
            v = vapi.get_firewall_rulenumber(hostname_default, firewall_name, rulenumber)
            if v.success:
                ruledata = v.data

                # if rule exists control variables are true
                rulenumber_valid = True
            else:
                msg.add_error("There is no rule number inside firewall")

    # mode add rule
    elif mode == "addrule":
        if request.POST.get('rulenumber', None) == None:
            #msg.add_error("Rule number empty")
            # before fill form rule number is empty
            pass
        else:
            rulenumber = request.POST.get('rulenumber')
            if int(rulenumber) >= 1 and int(rulenumber) <= 9999:
                rulenumber_valid = True
                rulenumber = request.POST.get('rulenumber')
            else:
                rulenumber_valid = False
                msg.add_error("Rule number must be between 1 and 9999")

    ###############################################################################################################################################################
    # update rule action
    if rulenumber_valid and request.POST.get('ruleaction', None) != None:
        if request.POST.get('ruleaction') in ["accept", "drop", "reject"]:
            if mode == "editrule" and ruledata['action'] and request.POST.get('ruleaction') == ruledata['action']:
                msg.add_debug("Action: not changed")
            else:
                v = vapi.set_firewall_rule_action(hostname_default, firewall_name, rulenumber, request.POST.get('ruleaction'))
                if v.success == False:
                    msg.add_error("Action: fail to change - " + v.reason)
                else:
                    # updating ruledata
                    ruledata['action'] = request.POST.get('ruleaction')
                    changed = True
                    msg.add_success("Action: updated")
        else:
            msg.add_error("Action invalid")

    ###############################################################################################################################################################
    # update rule status
    if rulenumber_valid and request.POST.get('status', None) != None:
        if mode == "editrule": 
            if request.POST.get('status') == "enable" and "disable" not in ruledata:
                msg.add_debug("Status: not changed")
            elif request.POST.get('status') == "disable" and "disable" in ruledata:
                msg.add_debug("Status: not changed")
            elif request.POST.get('status') == "disable" and "disable" not in ruledata:
                v = vapi.set_firewall_rule_disabled(hostname_default, firewall_name, rulenumber)
                if v.success == False:
                    msg.add_error("Status: failed to disable - " + v.reason)
                else:
                    # updating ruledata
                    ruledata['disable'] = {}
                    ruledata['status'] = 'disabled'
                    changed = True
                    msg.add_success("Status disabled")
            elif request.POST.get('status') == "enable" and "disable" in ruledata:
                v = vapi.set_firewall_rule_enabled(hostname_default, firewall_name, rulenumber)
                if v.success == False:
                    msg.add_error("Status: failed to enable - " + v.reason)
                else:
                    # updating ruledata
                    del ruledata['disable']
                    ruledata['status'] = 'enabled'
                    changed = True
                    msg.add_success("Status: enabled")                    
        elif mode == "addrule":
            if request.POST.get('status') == "disable":
                v = vapi.set_firewall_rule_disabled(hostname_default, firewall_name, rulenumber)
                if v.success == False:
                    msg.add_error("Status: failed to disable - " + v.reason)
                else:
                    # updating ruledata
                    ruledata['disable'] = {}
                    ruledata['status'] = 'disabled'
                    changed = True
                    msg.add_info("Status: disabled")
            else:
                # nothing to do if status = enable
                pass

    ###############################################################################################################################################################
    # update description
    if rulenumber_valid == True and request.POST.get('description', None) != None:
        if 'description' in ruledata and request.POST.get('description') == ruledata['description']:
            msg.add_debug("Description: not changed")
        else:
            v = vapi.set_firewall_rule_description(hostname_default, firewall_name, rulenumber, request.POST.get('description'))
            if v.success == False:
                msg.add_error("Description: failed to update")
            else:
                # updating ruledata
                ruledata['description'] = request.POST.get('description')
                changed = True
                msg.add_success("Description: updated")

    ###############################################################################################################################################################
    # update criteria_protocol
    if rulenumber_valid == True and request.POST.get('criteria_protocol', None) == "1":
        protocol_criteria = None
        protocol_criteria_delete = False

        # other protocol - todo validate data
        if request.POST.get('protocol_criteria', None) == "other":
            if request.POST.get('protocol_custom', None) != None:
                protocol_criteria = request.POST.get('protocol_custom')
        # delete protocol
        elif request.POST.get('protocol_criteria', None) == "none":
            protocol_criteria_delete = True

            if 'protocol' in ruledata:
                v = vapi.set_firewall_rule_protocol_delete(hostname_default, firewall_name, rulenumber)
                if v.success == False:
                    msg.add_error("Criteria Protocol: failed to unset - " + v.reason)
                else:
                    del ruledata['protocol']                   
                    changed = True
                    msg.add_success("Criteria Protocol: unset")
            else:
                msg.add_debug("Criteria Protocol:  not changed unset not needed")
        # common protocols
        elif request.POST.get('protocol_criteria', None) in ['all', 'tcp', 'udp', 'tcp_udp', 'icmp']:
            protocol_criteria = request.POST.get('protocol_criteria')
        # other cases did not checked anything


        if protocol_criteria != None:
            # negate protocol
            if request.POST.get('protocol_negate', None) == "1":
                protocol_negate = "!"
            else:
                protocol_negate = ""
            protocol_criteria_txt = protocol_negate + protocol_criteria

            if 'protocol' in ruledata and protocol_criteria_txt == ruledata['protocol']:
                msg.add_debug("Criteria Protocol:  not changed")
            else:
                v = vapi.set_firewall_rule_protocol(hostname_default, firewall_name, rulenumber, protocol_criteria_txt)
                if v.success == False:
                    msg.add_error("Criteria Protocol: failed to update - " + v.reason)
                else:
                    # updating ruledata
                    ruledata['protocol'] = protocol_criteria_txt
                    changed = True
                    msg.add_success("Criteria Protocol: updated")
        else:
            if protocol_criteria_delete != True:
                msg.add_error("Criteria Protocol: invalid protocol")
    
    ###############################################################################################################################################################
    # update criteria_port (True only to group if block on Visual Studio)
    if True:
        destinationport_json =  request.POST.get('destinationport_json', None)
        sourceport_json =       request.POST.get('sourceport_json', None)
        dport_form = []
        sport_form = []

        if destinationport_json != None:
            try:
                dport_form = json.loads(destinationport_json)
            except ValueError:
                pass
        if sourceport_json != None:
            try:
                sport_form = json.loads(sourceport_json)
            except ValueError:
                pass
        


        # remove ports unset
        dport_delete = []
        sport_delete = []

        if 'destination' in ruledata and 'port' in ruledata['destination']:
            dport_ruledata = ruledata['destination']['port'].split(",")
        else:
            dport_ruledata = []

        if 'source' in ruledata and 'port' in ruledata['source']:
            sport_ruledata = ruledata['source']['port'].split(",")
        else:
            sport_ruledata = []

        dport_changes = 0
        sport_changes = 0

        dport_delete_all = False
        sport_delete_all = False

        #msg.add_debug("Criteria Ports Destination: ports - " + pprint.pformat(dport_ruledata))
        #msg.add_debug("Criteria Ports Source: ports - " + pprint.pformat(sport_ruledata))

        # find ports to mark as removed
        if rulenumber_valid == True and request.POST.get('criteria_port', None) == "1":
            if len(sport_form) == 0:
                msg.add_debug("Criteria Ports Source: remove all ports")
                sport_ruledata = []
                sport_changes = sport_changes + 1
                sport_delete_all = True
            else:
                for port in sport_ruledata:
                    if port not in sport_form:
                        sport_ruledata.remove(port)   
                        sport_delete.append(port)   
                        sport_changes = sport_changes + 1
                for port in sport_form:
                    if port not in sport_ruledata:
                        sport_ruledata.append(port)   
                        sport_changes = sport_changes + 1

        if rulenumber_valid == True and request.POST.get('criteria_port', None) == "1":
            if len(dport_form) <= 0:
                msg.add_debug("Criteria Ports Destination: remove all ports")
                dport_ruledata = []
                dport_changes = dport_changes + 1 
                dport_delete_all = True
            else:
                for port in dport_ruledata:
                    if port not in dport_form:
                        dport_ruledata.remove(port)
                        dport_delete.append(port)   
                        dport_changes = dport_changes + 1 
                for port in dport_form:
                    if port not in dport_ruledata:
                        dport_ruledata.append(port)     
                        dport_changes = dport_changes + 1                     

        if len(dport_delete) > 0:
            msg.add_debug("Criteria Ports Destination: remove ports - " + ",".join(dport_delete))
        if len(sport_delete) > 0:
            msg.add_debug("Criteria Ports Source: remove ports - " + ",".join(sport_delete))        



        if rulenumber_valid == True and dport_changes > 0:
            if dport_delete_all == True:
                v = vapi.set_firewall_rule_destination_ports_delete(hostname_default, firewall_name, rulenumber)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Ports Destination: updated delete all destination success")
                    if 'destination' in ruledata and 'port' in ruledata['destination']:
                        del ruledata['destination']['port']
                else:
                    msg.add_error("Criteria Ports Destination: delete all failed - " + v.reason)

            else:
                msg.add_debug("Criteria Ports Destination: ports - " + ",".join(dport_ruledata))
                v = vapi.set_firewall_rule_destination_ports(hostname_default, firewall_name, rulenumber, dport_ruledata)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Ports Destination: updated")
                    ruledata['destination']['port'] = ','.join(dport_ruledata)
                else:
                    msg.add_error("Criteria Ports Destination: failed - " + v.reason)

        if rulenumber_valid == True and sport_changes > 0:
            if sport_delete_all == True:
                v = vapi.set_firewall_rule_source_ports_delete(hostname_default, firewall_name, rulenumber)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Ports Destination: updated delete all source success")
                    if 'source' in ruledata and 'port' in ruledata['source']:
                        del ruledata['source']['port']
                else:
                    msg.add_error("Criteria Ports Destination: delete all failed - " + v.reason)

            else:
                msg.add_debug("Criteria Ports Source: ports - " + ",".join(sport_ruledata))    
                v = vapi.set_firewall_rule_source_ports(hostname_default, firewall_name, rulenumber, sport_ruledata)
                if v.success:
                    changed = True 
                    msg.add_success("Criteria Ports Source: updated")
                    ruledata['source']['port'] = ','.join(sport_ruledata)
                else:
                    msg.add_error("Criteria Ports Source: failed - " + v.reason)
    
    ###############################################################################################################################################################
    # update criteria_tcpflags
    if request.POST.get('criteria_tcpflags', None) == "1":
        tcpflags_form = []
        
        if request.POST.get('tcpflags_syn', None) == "1":
            tcpflags_form.append('SYN')
        if request.POST.get('tcpflags_isyn', None) == "1":
            tcpflags_form.append('!SYN')                        
        
        if request.POST.get('tcpflags_ack', None) == "1":
            tcpflags_form.append('ACK')
        if request.POST.get('tcpflags_iack', None) == "1":
            tcpflags_form.append('!ACK')

        if request.POST.get('tcpflags_fin', None) == "1":
            tcpflags_form.append('FIN')
        if request.POST.get('tcpflags_ifin', None) == "1":
            tcpflags_form.append('!FIN')                        
        
        if request.POST.get('tcpflags_rst', None) == "1":
            tcpflags_form.append('RST')
        if request.POST.get('tcpflags_irst', None) == "1":
            tcpflags_form.append('!RST')

        if request.POST.get('tcpflags_urg', None) == "1":
            tcpflags_form.append('URG')
        if request.POST.get('tcpflags_iurg', None) == "1":
            tcpflags_form.append('!URG')                        

        if request.POST.get('tcpflags_psh', None) == "1":
            tcpflags_form.append('PSH')
        if request.POST.get('tcpflags_ipsh', None) == "1":
            tcpflags_form.append('!PSH')                        

        if request.POST.get('tcpflags_all', None) == "1":
            tcpflags_form.append('ALL')
        if request.POST.get('tcpflags_iall', None) == "1":
            tcpflags_form.append('!ALL')                                                
        

        # will need to empty tcpflags
        if 'tcp' in ruledata and 'flags' in ruledata['tcp']: 
            tcpflags_rule = ruledata['tcp']['flags'].split(',')
        else:
            tcpflags_rule = []

        if len(tcpflags_form) == 0 and len(tcpflags_rule) > 0:
            v = vapi.set_firewall_rule_tcpflags_delete(hostname_default, firewall_name, rulenumber)
            if v.success:
                changed = True
                msg.add_success("Criteria TCP Ports: empty tcp flags success")

                if 'tcp' in ruledata:
                    if 'flags' in ruledata['tcp']:
                        del ruledata['tcp']['flags']
            else:
                msg.add_error("Criteria TCP Ports: empty tcp failed - " + v.reason)
        elif len(tcpflags_form) > 0:
            v = vapi.set_firewall_rule_tcpflags(hostname_default, firewall_name, rulenumber, tcpflags_form)

            if v.success:
                changed = True
                msg.add_success("Criteria TCP Ports: updated success")

                if 'tcp' not in ruledata:
                    ruledata['tcp'] = {}
                ruledata['tcp']['flags'] = ",".join(tcpflags_form)
            else:
                msg.add_error("Criteria TCP Ports: updated failed - " + v.reason)

    ###############################################################################################################################################################
    # update criteria_address
    if request.POST.get('criteria_address', None) == "1":
        if request.POST.get('saddress', None) != None:              
            saddress = request.POST.get('saddress')
            if len(saddress.strip()) == 0:             
                v = vapi.set_firewall_rule_source_address_delete(hostname_default, firewall_name, rulenumber)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Source Address: clean success") 
                    if 'source' in ruledata:
                        if 'address' in ruledata['source']:
                            del ruledata['source']['address']
                else:
                    msg.add_error("Criteria Source Address: clean failed - " + v.reason)   
            else:    
                # negate saddress
                if request.POST.get('saddress_negate', None) == "1":
                    saddress_negate = "!"
                else:
                    saddress_negate = ""
                                            
                saddress_txt = saddress_negate + saddress
                
                v = vapi.set_firewall_rule_source_address(hostname_default, firewall_name, rulenumber, saddress_txt)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Source Address: updated success") 

                    if 'source' not in ruledata:
                        ruledata['source'] = {}
                    ruledata['source']['address'] = saddress_txt
                else:
                    msg.add_error("Criteria Source Address: updated failed - " + v.reason)


        if request.POST.get('daddress', None) != None:              
            daddress = request.POST.get('daddress')       
            if len(daddress.strip()) == 0:             
                v = vapi.set_firewall_rule_destination_address_delete(hostname_default, firewall_name, rulenumber)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Destination Address: clean success") 
                    if 'destination' in ruledata:
                        if 'address' in ruledata['destination']:
                            del ruledata['destination']['address']
                else:
                    msg.add_error("Criteria Destination Address: clean failed - " + v.reason)    
            else:
                # negate daddress_negate
                if request.POST.get('daddress_negate', None) == "1":
                    daddress_negate = "!"
                else:
                    daddress_negate = ""                    

                daddress_txt = daddress_negate + daddress

                v = vapi.set_firewall_rule_destination_address(hostname_default, firewall_name, rulenumber, daddress_txt)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Destination Address: updated success") 

                    if 'destination' not in ruledata:
                        ruledata['destination'] = {}
                    ruledata['destination']['address'] = daddress         
                else:
                    msg.add_error("Criteria Destination Address: updated failed - " + v.reason)                           

    ###############################################################################################################################################################
    # update criteria_addressgroup
    if request.POST.get('criteria_addressgroup', None) == "1":
        

        # source address
        if request.POST.get('saddressgroup', None) != None:              
            saddressgroup = request.POST.get('saddressgroup').strip()
        else:
            saddressgroup = ''

        saddressgroup_ruledata = ''
        if 'source' in ruledata:
            if 'group' in ruledata['source']:
                if 'address-group' in ruledata['source']['group']:
                    saddressgroup_ruledata = ruledata['source']['group']['address-group']

        if len(saddressgroup) == 0: 
            v = vapi.set_firewall_rule_source_addressgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Address Group: delete success") 

                if 'source' in ruledata:
                    if 'group' in ruledata['source']:
                        if 'address-group' in ruledata['source']['group']:
                            del ruledata['source']['group']['address-group']
            else:
                msg.add_error("Criteria Source Address Group: delete failed - " + v.reason)         

        elif saddressgroup != saddressgroup_ruledata:
            v = vapi.set_firewall_rule_source_addressgroup(hostname_default, firewall_name, rulenumber, saddressgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Address Group: updated success") 

                if 'source' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['source']:
                    ruledata['source']['group'] = {}
                ruledata['source']['group']['address-group'] = saddressgroup         
            else:
                msg.add_error("Criteria Source Address Group: updated failed - " + v.reason)         


        # destination address
        if request.POST.get('daddressgroup', None) != None:              
            daddressgroup = request.POST.get('daddressgroup').strip()
        else:
            daddressgroup = ''


        daddressgroup_ruledata = ''
        if 'destination' in ruledata:
            if 'group' in ruledata['destination']:
                if 'address-group' in ruledata['destination']['group']:
                    daddressgroup_ruledata = ruledata['destination']['group']['address-group']

        if len(daddressgroup) == 0: 
            v = vapi.set_firewall_rule_destination_addressgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Address Group: delete success") 

                if 'destination' in ruledata:
                    if 'group' in ruledata['destination']:
                        if 'address-group' in ruledata['destination']['group']:
                            del ruledata['destination']['group']['address-group']
            else:
                msg.add_error("Criteria Destination Address Group: delete failed - " + v.reason)         
        elif daddressgroup != daddressgroup_ruledata:
            v = vapi.set_firewall_rule_destination_addressgroup(hostname_default, firewall_name, rulenumber, daddressgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Address Group: updated success") 

                if 'destination' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['destination']:
                    ruledata['destination']['group'] = {}
                ruledata['destination']['group']['address-group'] = daddressgroup              
            else:
                msg.add_error("Criteria Destination Address Group: updated failed - " + v.reason)         

    ###############################################################################################################################################################
    # update criteria_networkgroup
    if request.POST.get('criteria_networkgroup', None) == "1":
    
        # source group
        if request.POST.get('snetworkgroup', None) != None:              
            snetworkgroup = request.POST.get('snetworkgroup').strip()
        else:
            snetworkgroup = ''

        snetworkgroup_ruledata = ''
        if 'source' in ruledata:
            if 'group' in ruledata['source']:
                if 'network-group' in ruledata['source']['group']:
                    snetworkgroup_ruledata = ruledata['source']['group']['network-group']

        if len(snetworkgroup) == 0: 
            v = vapi.set_firewall_rule_source_networkgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Network Group: delete success") 

                if 'source' in ruledata:
                    if 'group' in ruledata['source']:
                        if 'network-group' in ruledata['source']['group']:
                            del ruledata['source']['group']['network-group']
            else:
                msg.add_error("Criteria Source Network Group: delete failed - " + v.reason)         

        elif snetworkgroup != snetworkgroup_ruledata:
            v = vapi.set_firewall_rule_source_networkgroup(hostname_default, firewall_name, rulenumber, snetworkgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Network Group: updated success") 

                if 'source' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['source']:
                    ruledata['source']['group'] = {}
                ruledata['source']['group']['network-group'] = snetworkgroup         
            else:
                msg.add_error("Criteria Source Network Group: updated failed - " + v.reason) 


        # destination group
        if request.POST.get('dnetworkgroup', None) != None:              
            dnetworkgroup = request.POST.get('dnetworkgroup').strip()
        else:
            dnetworkgroup = ''

        dnetworkgroup_ruledata = ''
        if 'destination' in ruledata:
            if 'group' in ruledata['destination']:
                if 'network-group' in ruledata['destination']['group']:
                    dnetworkgroup_ruledata = ruledata['destination']['group']['network-group']

        if len(dnetworkgroup) == 0: 
            v = vapi.set_firewall_rule_destination_networkgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Network Group: delete success") 

                if 'destination' in ruledata:
                    if 'group' in ruledata['destination']:
                        if 'network-group' in ruledata['destination']['group']:
                            del ruledata['destination']['group']['network-group']
            else:
                msg.add_error("Criteria Destination Network Group: delete failed - " + v.reason)         
        elif dnetworkgroup != dnetworkgroup_ruledata:
            v = vapi.set_firewall_rule_destination_networkgroup(hostname_default, firewall_name, rulenumber, dnetworkgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Network Group: updated success") 

                if 'destination' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['destination']:
                    ruledata['destination']['group'] = {}
                ruledata['destination']['group']['network-group'] = dnetworkgroup              
            else:
                msg.add_error("Criteria Destination Network Group: updated failed - " + v.reason)         

    ###############################################################################################################################################################
    # update criteria_portgroup
    if request.POST.get('criteria_portgroup', None) == "1":
    
        # source port
        if request.POST.get('sportgroup', None) != None:              
            sportgroup = request.POST.get('sportgroup').strip()
        else:
            sportgroup = ''

        sportgroup_ruledata = ''
        if 'source' in ruledata:
            if 'group' in ruledata['source']:
                if 'port-group' in ruledata['source']['group']:
                    sportgroup_ruledata = ruledata['source']['group']['port-group']

        if len(sportgroup) == 0: 
            v = vapi.set_firewall_rule_source_portgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Port Group: delete success") 

                if 'source' in ruledata:
                    if 'group' in ruledata['source']:
                        if 'port-group' in ruledata['source']['group']:
                            del ruledata['source']['group']['port-group']
            else:
                msg.add_error("Criteria Source Port Group: delete failed - " + v.reason)         

        elif sportgroup != sportgroup_ruledata:
            v = vapi.set_firewall_rule_source_portgroup(hostname_default, firewall_name, rulenumber, sportgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Source Port Group: updated success") 

                if 'source' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['source']:
                    ruledata['source']['group'] = {}
                ruledata['source']['group']['port-group'] = sportgroup         
            else:
                msg.add_error("Criteria Source Port Group: updated failed - " + v.reason) 


        # destination port
        if request.POST.get('dportgroup', None) != None:              
            dportgroup = request.POST.get('dportgroup').strip()
        else:
            dportgroup = ''

        dportgroup_ruledata = ''
        if 'destination' in ruledata:
            if 'group' in ruledata['destination']:
                if 'port-group' in ruledata['destination']['group']:
                    dportgroup_ruledata = ruledata['destination']['group']['port-group']

        if len(dportgroup) == 0: 
            v = vapi.set_firewall_rule_destination_portgroup_delete(hostname_default, firewall_name, rulenumber)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Port Group: delete success") 

                if 'destination' in ruledata:
                    if 'group' in ruledata['destination']:
                        if 'port-group' in ruledata['destination']['group']:
                            del ruledata['destination']['group']['port-group']
            else:
                msg.add_error("Criteria Destination Port Group: delete failed - " + v.reason)         
        elif dportgroup != dportgroup_ruledata:
            v = vapi.set_firewall_rule_destination_portgroup(hostname_default, firewall_name, rulenumber, dportgroup)
            if v.success:   
                changed = True
                msg.add_success("Criteria Destination Port Group: updated success") 

                if 'destination' not in ruledata:
                    ruledata['source'] = {}
                if 'group' not in ruledata['destination']:
                    ruledata['destination']['group'] = {}
                ruledata['destination']['group']['port-group'] = dportgroup              
            else:
                msg.add_error("Criteria Destination Port Group: updated failed - " + v.reason) 

    ###############################################################################################################################################################
    # update criteria_sourcemac
    if request.POST.get('criteria_sourcemac', None) == "1":
        if request.POST.get('smac_source', None) != None:              
            smac = request.POST.get('smac_source')
            smac = smac.replace("-",":")
            smac = smac.lower()

            if len(smac.strip()) == 0:             
                v = vapi.set_firewall_rule_source_mac_delete(hostname_default, firewall_name, rulenumber)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Source Mac Address: clean success") 
                    if 'source' in ruledata:
                        if 'mac-address' in ruledata['source']:
                            del ruledata['source']['mac-address']
                else:
                    msg.add_error("Criteria Source Mac Address: clean failed - " + v.reason)   
            else:    
                # negate smac
                if request.POST.get('smac_source_negate', None) == "1":
                    smac_negate = "!"
                else:
                    smac_negate = ""
                                            
                smac_txt = smac_negate + smac              
                smac_original = ''
                if 'source' in ruledata:
                    if 'mac-address' in ruledata['source']:
                        smac_original = ruledata['source']['mac-address']

                if smac_txt != smac_original:
                    v = vapi.set_firewall_rule_source_mac(hostname_default, firewall_name, rulenumber, smac_txt)
                    if v.success:
                        changed = True
                        msg.add_success("Criteria Source Mac Address: updated success") 

                        if 'source' not in ruledata:
                            ruledata['source'] = {}
                        ruledata['source']['mac-address'] = smac_txt
                    else:
                        msg.add_error("Criteria Source Mac Address: updated failed - " + v.reason)

    ###############################################################################################################################################################
    # update criteria_packetstate
    if request.POST.get('criteria_packetstate', None) == "1":
        packetstates_all = ['established', 'invalid', 'new', 'related']

        packetstates_form = []
        packetstates_add = []
        packetstates_delete = []
        
        if request.POST.get('packetstate_established', None) == "1":
            packetstates_form.append('established')

        if request.POST.get('packetstate_invalid', None) == "1":
            packetstates_form.append('invalid')

        if request.POST.get('packetstate_new', None) == "1":
            packetstates_form.append('new')

        if request.POST.get('packetstate_related', None) == "1":
            packetstates_form.append('related')

        if len(packetstates_form) == 0:
            if 'state' in ruledata:
                for pstate in ruledata['state']:
                    packetstates_delete.append(pstate)

        if len(packetstates_form) > 0:
            for pstate in packetstates_all:
                # check what to add
                if 'state' not in ruledata:
                    if pstate in packetstates_form:
                        packetstates_add.append(pstate)
                else:
                    if pstate not in ruledata['state']:
                        if pstate in packetstates_form:
                            packetstates_add.append(pstate)
                    else:
                        if ruledata['state'][pstate] != 'enable':
                            if pstate in packetstates_form:
                                packetstates_add.append(pstate)

                # check what to delete
                if 'state' in ruledata:
                    if pstate in ruledata['state']:
                        if ruledata['state'][pstate] == 'enable':
                            if pstate not in packetstates_form:
                                    packetstates_delete.append(pstate)


            if 'state' not in ruledata:
                ruledata['state'] = {}
            
            for pstate in packetstates_add:
                v = vapi.set_firewall_rule_packetstate(hostname_default, firewall_name, rulenumber, pstate)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Packet State: state added") 
                    ruledata['state'][pstate] = 'enable'

            for pstate in packetstates_delete:
                v = vapi.set_firewall_rule_packetstate_delete(hostname_default, firewall_name, rulenumber, pstate)
                if v.success:
                    changed = True
                    msg.add_success("Criteria Packet State: state delete") 
                    if pstate in ruledata['state']:
                        del ruledata['state'][pstate]

    if changed == True:
        msg.add_success("Firewall rule saved")
        

    ruledata_json = json.dumps(ruledata)
    #vmsg.log("json", ruledata_json)

    template = loader.get_template("firewall/editrule.html")
    context = { 
        #'interfaces': interfaces,
        'instances':                        all_instances,
        'hostname_default':                 hostname_default,
        'firewall_name':                    firewall_name,
        'username':                         request.user,
        'is_superuser' :                    is_superuser,
        'services' :                        netservices['services'],
        'services_common' :                 netservices['common'],
        'firewall_networkgroup':            firewall_group['network-group'],
        'firewall_addressgroup':            firewall_group['address-group'],
        'firewall_portgroup':               firewall_group['port-group'],
        'mode' :                            mode,
        'msg' :                             msg.get_all(),
        'ruledata' :                        ruledata,
        'ruledata_pretty' :                 pprint.pformat(ruledata, indent=4, width=120),
        'ruledata_json' :                   ruledata_json,
        'rulenumber' :                      rulenumber,
    }

    return HttpResponse(template.render(context, request))
    
@is_authenticated
def addrule(request, firewall_name):
    return changerule(request, firewall_name, mode="addrule", rulenumber=None)

@is_authenticated
def editrule(request, firewall_name, rulenumber):
    return changerule(request, firewall_name, mode="editrule", rulenumber=rulenumber)

@is_authenticated
def show(request, firewall_name):
        
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    firewall = vyos.get_firewall(hostname_default, firewall_name)
    

    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_portgroup_list(request):
        
    hostname_default = vyos.get_hostname_prefered(request)
    firewall_portgroup = vyos.get_firewall_portgroup(hostname_default)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    template = loader.get_template('firewall/portgroup-list.html')
    context = { 
        'firewall_portgroup': firewall_portgroup,
        'hostname_default': hostname_default,
        'username': request.user, 
        'instances': all_instances,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_portgroup_del(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    vyos.set_firewall_portgroup_del(hostname_default, groupname)
    return redirect('firewall:firewall-portgroup-list')

@is_authenticated
def firewall_portgroup_add(request):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)
    netservices = network.get_services()

    if request.POST.get('name', None) != None and request.POST.get('portgroup_ports_hidden', None) != None and request.POST.get('portgroup_ports_hidden') != '':

        try:
            ports = json.loads(request.POST.get('portgroup_ports_hidden'))
        except ValueError:
            return redirect('firewall:firewall-portgroup-list')

        for port in ports:
            vyos.set_firewall_portgroup_add(hostname_default, request.POST.get('name'), port)

        if request.POST.get('description', None) != None:
            vyos.set_firewall_portgroup_description(hostname_default, request.POST.get('name'), request.POST.get('description'))

        return redirect('firewall:firewall-portgroup-list')



    template = loader.get_template('firewall/portgroup-add.html')
    context = { 
        'hostname_default': hostname_default,
        'username': request.user,        
        'instances': all_instances,
        'is_superuser' : is_superuser,
        'services_common' : netservices['common'],
        'services' : netservices['services'],
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_portgroup_edit(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)
    netservices = network.get_services()
    portgroups = vyos.get_firewall_portgroup(hostname_default)
    portgroups_json = json.dumps(portgroups['port-group'][groupname], separators=(',', ':'))
    description = portgroups['port-group'][groupname]['description']

    if request.POST.get('description', None) != None:
        vyos.set_firewall_portgroup_description(hostname_default, groupname, request.POST.get('description'))

    if request.POST.get('portgroup_ports_hidden', None) != None and request.POST.get('portgroup_ports_hidden') != '':

        try:
            ports = json.loads(request.POST.get('portgroup_ports_hidden'))
        except ValueError:
            return redirect('firewall:firewall-portgroup-list')

        port_remove = []
        port_add = []
        # each port in vyos database
        for port in portgroups['port-group'][groupname]['port']:
            # vyos port not in form
            if port not in ports:
                # so mark to remove
                port_remove.append(port)

        # each port comming from form
        for port in ports:
            # form port not in vyos database
            if port not in portgroups['port-group'][groupname]['port']:
                # so mark to add
                port_add.append(port)

        # add ports to vyos database
        for port in port_add:
            vyos.set_firewall_portgroup_add(hostname_default, groupname, port)

        # remove ports to vyos database
        for port in port_remove:
            vyos.set_firewall_portgroup_delete_port(hostname_default, groupname, port)

        if request.POST.get('description', None) != None:
            vyos.set_firewall_portgroup_description(hostname_default, request.POST.get('name'), request.POST.get('description'))

        return redirect('firewall:firewall-portgroup-list')




    template = loader.get_template('firewall/portgroup-edit.html')
    context = { 
        'hostname_default': hostname_default,
        'username': request.user,        
        'instances': all_instances,
        'is_superuser' : is_superuser,
        'groupname' : groupname,
        'services_common' : netservices['common'],
        'services' : netservices['services'],
        'description' : description,
        'portgroups_json' : portgroups_json,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_networkgroup_list(request):
        
    hostname_default = vyos.get_hostname_prefered(request)
    firewall_networkgroup = vyos.get_firewall_networkgroup(hostname_default)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    template = loader.get_template('firewall/networkgroup-list.html')
    context = { 
        'firewall_networkgroup': firewall_networkgroup,
        'hostname_default': hostname_default,
        'username': request.user, 
        'instances': all_instances,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_networkgroup_add(request):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    if (    request.POST.get('name', None) != None 
        and request.POST.get('networkgroup_json', None) != None):

        group =         request.POST.get('name', None)
        description =   request.POST.get('description', None)
        try:
            networks = json.loads(request.POST.get('networkgroup_json'))
        except ValueError:
            networks = {}


        changed = False

        vmsg.log('networks', networks)

        for network in networks:
            v = vapilib.api (
                hostname=   hostname_default,
                api =       "post",
                op =        "set",
                cmd =       ["firewall", "group", "network-group", group, "network", network],
                description = "add network-group network",
            )
            if v.success and changed == False:
                changed = True
            
        # set network description if it was created
            if changed == True:
                v = vapilib.api (
                    hostname=   hostname_default,
                    api =       "post",
                    op =        "set",
                    cmd =       ["firewall", "group", "network-group", group, "description", description],
                    description = "set network-group description",
                )

                return redirect('firewall:firewall-networkgroup-list')



    template = loader.get_template('firewall/networkgroup-add.html')
    context = { 
        'hostname_default': hostname_default,
        'username': request.user,        
        'instances': all_instances,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_networkgroup_del(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    vyos.set_firewall_networkgroup_del(hostname_default, groupname)
    return redirect('firewall:firewall-networkgroup-list')

@is_authenticated
def firewall_addressgroup_list(request):
        
    hostname_default = vyos.get_hostname_prefered(request)
    firewall_addressgroup = vyos.get_firewall_addressgroup(hostname_default)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    template = loader.get_template('firewall/addressgroup-list.html')
    context = { 
        'firewall_addressgroup': firewall_addressgroup,
        'hostname_default': hostname_default,
        'username': request.user,        
        'instances': all_instances,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_addressgroup_add(request):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    if (    request.POST.get('name', None) != None 
        and request.POST.get('addressgroup_json', None) != None):

        group =         request.POST.get('name', None)
        description =   request.POST.get('description', None)
        try:
            networks = json.loads(request.POST.get('addressgroup_json'))
        except ValueError:
            networks = {}


        changed = False

        vmsg.log('networks', networks)

        for network in networks:
            v = vapilib.api (
                hostname =  hostname_default,
                api =       "post",
                op =        "set",
                cmd =       ["firewall", "group", "address-group", group, "address", network],
                description = "add address-group network",
            )
            if v.success and changed == False:
                changed = True
            
        # set network description if it was created
        if changed == True:
            if description != None:
                v = vapilib.api (
                    hostname=   hostname_default,
                    api =       "post",
                    op =        "set",
                    cmd =       ["firewall", "group", "address-group", group, "description", description],
                    description = "set address-group description",
                )

            return redirect('firewall:firewall-addressgroup-list')


    template = loader.get_template('firewall/addressgroup-add.html')
    context = { 
        'hostname_default': hostname_default,
        'username': request.user,        
        'instances': all_instances,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_addressgroup_del(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    vyos.set_firewall_addressgroup_del(hostname_default, groupname)
    return redirect('firewall:firewall-addressgroup-list')

@is_authenticated
def firewall_addressgroup_desc(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)

    v = vapilib.api (
        hostname=   hostname_default,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "group", "address-group", groupname],
        description = "show address-group config",
    )
    groupinfo = v.data
    if 'address' not in groupinfo:
        networks_original = []
    else:
        networks_original = groupinfo['address']

        if type(networks_original) is str:
            vmsg.log("tipo", type(networks_original))
            networks_original = [groupinfo['address']]
        else:
            networks_original = groupinfo['address']

    vmsg.log("networks_original", networks_original)

    networks_json = json.dumps(networks_original)


    changed = False

    if v.success:
        if request.POST.get('description', None) != None:
            v = vapilib.api (
                hostname=   hostname_default,
                api =       "post",
                op =        "set",
                cmd =       ["firewall", "group", "address-group", groupname, "description", request.POST.get('description')],
                description = "set network-group description",
            )
            changed = True


        if request.POST.get('networkgroup_json', None) != None:
            try:
                networks_new = json.loads(request.POST.get('networkgroup_json'))
            except ValueError:
                networks_new = {}

            vmsg.log('networks new', networks_new)

            for network in networks_new:
                v = vapilib.api (
                    hostname=   hostname_default,
                    api =       "post",
                    op =        "set",
                    cmd =       ["firewall", "group", "address-group", groupname, "address", network],
                    description = "edit address-group network",
                )
                if v.success and changed == False:
                    changed = True
            
            vmsg.log('networks original', networks_original)

            for network in networks_original:
                if network not in networks_new:
                    v = vapilib.api (
                        hostname=   hostname_default,
                        api =       "post",
                        op =        "delete",
                        cmd =       ["firewall", "group", "address-group", groupname, "address", network],
                        description = "delete address-group network",
                    )
                    if v.success and changed == False:
                        changed = True

        if changed == True:
            return redirect('firewall:firewall-addressgroup-list')


        template = loader.get_template('firewall/addressgroup-desc.html')
        context = { 
            'groupinfo': groupinfo,
            'hostname_default': hostname_default,
            'username': request.user,        
            'instances': all_instances,
            'is_superuser' : is_superuser,
            'groupname': groupname,
            'networks_json' : networks_json,
        }   
        return HttpResponse(template.render(context, request))
    else:
        return redirect('firewall:firewall-addressgroup-list')    

@is_authenticated
def firewall_networkgroup_desc(request, groupname):
    hostname_default = vyos.get_hostname_prefered(request)
    all_instances = vyos.instance_getall_by_group(request)
    is_superuser = perms.get_is_superuser(request.user)


    v = vapilib.api (
        hostname=   hostname_default,
        api =       "get",
        op =        "showConfig",
        cmd =       ["firewall", "group", "network-group", groupname],
        description = "show network-group config",
    )
    groupinfo = v.data
    if 'network' not in groupinfo:
        networks_original = []
    else:
        networks_original = groupinfo['network']

        if type(networks_original) is str:
            vmsg.log("tipo", type(networks_original))
            networks_original = [groupinfo['network']]
        else:
            networks_original = groupinfo['network']

    vmsg.log("networks_original", networks_original)

    networks_json = json.dumps(networks_original)


    changed = False

    if v.success:
        if request.POST.get('description', None) != None:
            v = vapilib.api (
                hostname=   hostname_default,
                api =       "post",
                op =        "set",
                cmd =       ["firewall", "group", "network-group", groupname, "description", request.POST.get('description')],
                description = "set network-group description",
            )
            changed = True


        if request.POST.get('networkgroup_json', None) != None:
            try:
                networks_new = json.loads(request.POST.get('networkgroup_json'))
            except ValueError:
                networks_new = {}

            vmsg.log('networks new', networks_new)

            for network in networks_new:
                v = vapilib.api (
                    hostname=   hostname_default,
                    api =       "post",
                    op =        "set",
                    cmd =       ["firewall", "group", "network-group", groupname, "network", network],
                    description = "edit network-group network",
                )
                if v.success and changed == False:
                    changed = True
            
            vmsg.log('networks original', networks_original)

            for network in networks_original:
                if network not in networks_new:
                    v = vapilib.api (
                        hostname=   hostname_default,
                        api =       "post",
                        op =        "delete",
                        cmd =       ["firewall", "group", "network-group", groupname, "network", network],
                        description = "delete network-group network",
                    )
                    if v.success and changed == False:
                        changed = True

        if changed == True:
            return redirect('firewall:firewall-networkgroup-list')


        template = loader.get_template('firewall/networkgroup-desc.html')
        context = { 
            'groupinfo': groupinfo,
            'hostname_default': hostname_default,
            'username': request.user,        
            'instances': all_instances,
            'is_superuser' : is_superuser,
            'groupname': groupname,
            'networks_json' : networks_json,
        }   
        return HttpResponse(template.render(context, request))
    else:
        return redirect('firewall:firewall-networkgroup-list')

@is_authenticated
def firewall_config(request, firewall_name):  
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)
    
    firewall = vyos.get_firewall(hostname_default, firewall_name)
    

    template = loader.get_template('firewall/show.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall':  firewall,
        'firewall_name': firewall_name,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_global(request):
   
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    if int(request.POST.get('allping', 0)) == 1:
        vyos.set_firewall_allping_enable(hostname_default)
    else:
        vyos.set_firewall_allping_disable(hostname_default)

    if int(request.POST.get('syncookies', 0)) == 1:
        vyos.set_firewall_syncookies_enable(hostname_default)
    else:
        vyos.set_firewall_syncookies_disable(hostname_default)

    
    return redirect('firewall:firewall-list')

@is_authenticated
def firewall_remove(request, firewall_name):
       
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)

    firewall = vyos.delete_firewall(hostname_default, firewall_name)
    
    return redirect('firewall:firewall-list')

@is_authenticated
def firewall_edit(request, firewall_name):
   
    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    firewall = vyos.get_firewall(hostname_default, firewall_name)
    firewall['defaultaction'] = firewall['default-action']
    is_superuser = perms.get_is_superuser(request.user)

    changed = False
    if 'description' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "description", request.POST['description']]}
        result2 = vyos.set_config(hostname_default, cmd)
        print(result2)
        changed = True

    if 'action' in request.POST:
        cmd = {"op": "set", "path": ["firewall", "name", firewall_name, "default-action", request.POST['action']]}
        result3 = vyos.set_config(hostname_default, cmd)
        print(result3)
        changed = True

    if changed == True:
        return redirect('firewall:firewall-list')

    template = loader.get_template('firewall/edit.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_name': firewall_name,
        'firewall': firewall,
        'username': request.user,
        'is_superuser' : is_superuser,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_zones(request):
    # basic methods all views should call
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    # local methods to prepare env
    get_firewall_zones      = vapi.get_firewall_zones(hostname_default) # get all zones since we cannot allow an interface belongs more than one zone

    interfaces_defined          = []
    interfaces_defined_form     = []
    interfaces_zone             = {}
    allzones                    = []
    allzonesrules               = []

    if get_firewall_zones.success:
        allzones = get_firewall_zones.data
        if 'zone' in allzones:
            for zone in allzones['zone']:
                if 'interface' in allzones['zone'][zone]:
                    for zoneinterface in allzones['zone'][zone]['interface']:
                        interfaces_defined.append(zoneinterface)
                        interfaces_defined_form.append("interface_" + zoneinterface)
                        interfaces_zone[zoneinterface] = zone
                if 'from' in allzones['zone'][zone]:
                    zonerule = {}
                    zonerule['dstzone'] = zone

                    for zonesrc in allzones['zone'][zone]['from']:
                        zonerule['srczone'] =       zonesrc

                        if 'firewall' in allzones['zone'][zone]['from'][zonesrc]:
                            if 'name' in allzones['zone'][zone]['from'][zonesrc]['firewall']:
                                zonerule['firewall'] =       allzones['zone'][zone]['from'][zonesrc]['firewall']['name']

                    allzonesrules.append(zonerule)

                    

    if 'zone' in allzones:
        allzones2 = []
        for zone in allzones['zone']:
            zonec = allzones['zone'][zone]
            zonec['name'] = zone
            allzones2.append(zonec)
            

    template = loader.get_template('firewall/zones.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                                all_instances,
        'hostname_default':                         hostname_default,
        'username':                                 request.user,
        'is_superuser' :                            is_superuser,
        'allzones':                                 allzones2,
        'allzones_pretty':                          pprint.pformat(allzones2, indent=4, width=120),
        'allzonesrules' :                           allzonesrules,

    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_zones_add(request):
    msg = vmsg.msg()

    # basic methods all views should call
    all_instances       = vyos.instance_getall()
    hostname_default    = vyos.get_hostname_prefered(request)
    is_superuser        = perms.get_is_superuser(request.user)

    # local methods to prepare env
    interfaces              = vyos.get_interfaces(hostname_default)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)
    get_firewall_zones      = vapi.get_firewall_zones(hostname_default) # get all zones since we cannot allow an interface belongs more than one zone

    interfaces_defined          = []
    interfaces_defined_form     = []
    interfaces_zone             = {}
    allzones                    = []

    if get_firewall_zones.success:
        allzones = get_firewall_zones.data
        if 'zone' in allzones:
            for zone in allzones['zone']:
                if 'interface' in allzones['zone'][zone]:
                    for zoneinterface in allzones['zone'][zone]['interface']:
                        interfaces_defined.append(zoneinterface)
                        interfaces_defined_form.append("interface_" + zoneinterface)
                        interfaces_zone[zoneinterface] = zone

    # local control vars
    valid               = False
    localzone           = False

    if request.POST.get('name', None) != None:
        zonename = request.POST.get('name')
        zonename = zonename.strip()

        if request.POST.get('localzone', None) != None:
            # set local-zone
            v = vapi.set_firewall_zone_localzone(hostname_default, zonename)
            if v.success:   
                valid = True
                msg.add_success("Local-zone defined")       
            else:
                msg.add_error("Local-zone failed to set") 
        else:
            # add all interfaces
            interfaces_form = []
            for rv in request.POST:
                iface_form = None
                if rv.startswith("interface_"):
                    rvprefixlen = len("interface_")
                    iface_form = rv[rvprefixlen:]
                    interfaces_form.append(iface_form)

                    v = vapi.set_firewall_zone_interface(hostname_default, zonename, iface_form)
                    if v.success:   
                        valid = True
                        msg.add_success("Interface added to zone: " +  iface_form)
                    else:
                        msg.add_error("Interface not added to zone: " +  iface_form + " - "  + v.reason)

            if valid == True:
                # if editing remove localzone if set
                pass


        if valid == True:
            if request.POST.get('description', None) != None:
                zonedescription = request.POST.get('description')
                zonedescription = zonedescription.strip()
                if len(zonedescription) > 0:
                    v = vapi.set_firewall_zone_description(hostname_default, zonename, zonedescription)
                    if v.success:   
                        valid = True
                        msg.add_success("Description defined")
                    else:
                        msg.add_error("Description failed to set")

            if request.POST.get('action', None) != None:
                zoneaction = request.POST.get('action')
                zoneaction = zoneaction.strip()
                if zoneaction in ['drop', 'reject']:
                    v = vapi.set_firewall_zone_defaultaction(hostname_default, zonename, zoneaction)
                    if v.success:   
                        valid = True
                        msg.add_success("Default action defined")       
                    else:
                        msg.add_error("Default action failed to set")                        


            msg.add_success("Zone added") 

    template = loader.get_template('firewall/zones-add.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                    all_instances,
        'hostname_default':             hostname_default,
        'username':                     request.user,
        'is_superuser':                 is_superuser,
        'interfaces':                   interfaces,
        'interfaces_pretty':            pprint.pformat(interfaces, indent=4, width=120),
        'interfaces_all_names_pretty':  pprint.pformat(interfaces_all_names, indent=4, width=120),
        'interfaces_all_names':         interfaces_all_names,
        'msg' :                         msg.get_all(),
        'allzones':                     allzones,
        'interfaces_defined':           interfaces_defined,
        'interfaces_defined_form':      interfaces_defined_form,
        'interfaces_zone':              interfaces_zone,
        'form_added':                   valid,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_zones_edit(request, zonename):
    # validation
    zonename = zonename.strip()
    


    msg = vmsg.msg()
    
    # basic methods all views should call
    all_instances       = vyos.instance_getall()
    hostname_default    = vyos.get_hostname_prefered(request)
    is_superuser        = perms.get_is_superuser(request.user)

    # local methods to prepare env
    interfaces              = vyos.get_interfaces(hostname_default)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)
    get_firewall_zones      = vapi.get_firewall_zones(hostname_default) # get all zones since we cannot allow an interface belongs more than one zone
    get_firewall_zone       = vapi.get_firewall_zone(hostname_default, zonename)
    zoneinfo                = get_firewall_zone.data

    form_changed = False
    if request.POST.get('form_changed', None) == "1":
        form_changed = True

    # set interface_alias in format eth0 if has not vif and eth0.vlan if has vlan
    for iname in interfaces_all_names:
        if 'vif' in iname:
            iname['interface_alias'] = "{interface_name}.{vif}".format(interface_name=iname['interface_name'], vif=iname['vif'])
        else:
            iname['interface_alias'] = iname['interface_name']


    # create a dict
    interfaces_all_names_dict = {}
    for iname in interfaces_all_names:
        if 'vif' in iname:
            ialias = "{interface_name}.{vif}".format(interface_name=iname['interface_name'], vif=iname['vif'])
        else:
            ialias = iname['interface_name']

        interfaces_all_names_dict[ialias] = iname



    if zoneinfo == None:
        msg.add_error("Zone not exists")
        template = loader.get_template('firewall/zones-edit.html')
        context = { 
            #'interfaces': interfaces,
            'instances':                    all_instances,
            'hostname_default':             hostname_default,
            'username':                     request.user,
            'is_superuser':                 is_superuser,
            'interfaces':                   interfaces,
            'interfaces_all_names_pretty':  pprint.pformat(interfaces_all_names, indent=4, width=120),
            'interfaces_all_names':         interfaces_all_names,
            'msg' :                         msg.get_all(),
            "zoneinfo":                     zoneinfo,
            "zonename":                     zonename,
            "exists":                       False
        }   
        return HttpResponse(template.render(context, request))



    interfaces_defined              = []
    interfaces_defined_form         = []
    allzones                        = []

    interfaces_zone_alias           = []
    interfaces_zone_alias_other     = []
    interfaces_zone                 = []
    interfaces_zone_other           = []

    if get_firewall_zones.success:
        allzones = get_firewall_zones.data
        if 'zone' in allzones:
            for zone in allzones['zone']:
                if 'interface' in allzones['zone'][zone]:
                    if isinstance(allzones['zone'][zone]['interface'], list):
                        for zoneinterface in allzones['zone'][zone]['interface']:
                            if zone == zonename:
                                #print("@@@", zone, zoneinterface)
                                interfaces_zone_alias.append("interface_" + zoneinterface)
                                interfaces_zone.append(zoneinterface)
                            else:
                                interfaces_zone_alias_other.append("interface_" + zoneinterface)
                                interfaces_zone_other.append(zoneinterface)

                            interfaces_defined.append(zoneinterface)
                            interfaces_defined_form.append("interface_" + zoneinterface)
                    else:
                        zoneinterface = allzones['zone'][zone]['interface']
                        if zone == zonename:
                           # print("@@@", zone, zoneinterface)
                            interfaces_zone_alias.append("interface_" + zoneinterface)
                            interfaces_zone.append(zoneinterface)
                        else:
                            interfaces_zone_alias_other.append("interface_" + zoneinterface)
                            interfaces_zone_other.append(zoneinterface)
  

                        interfaces_defined.append(zoneinterface)
                        interfaces_defined_form.append("interface_" + zoneinterface)
                            
    

    # local control vars
    valid               = False
    localzone           = False


    # add all interfaces
    interfaces_form = []
    for rv in request.POST:
        iface_form = None
        if rv.startswith("interface_"):
            rvprefixlen = len("interface_")
            iface_form = rv[rvprefixlen:]
            interfaces_form.append(iface_form)

    # each interface unset on form we need to delete from zone
    if form_changed:                
        for iface in interfaces_all_names:
            # interface belongs to zone currently
            if iface["interface_alias"] in interfaces_zone:
                # interface not marked on form
                if iface["interface_alias"] not in interfaces_form:
                    v = vapi.delete_firewall_zone_interface(hostname_default, zonename, iface["interface_alias"])
                    if v.success:   
                        valid = True
                        msg.add_success("Interface {iface} removed from zone.".format(iface=iface["interface_alias"]))
                        zalias = "interface_" + iface["interface_alias"]
                        if zalias in interfaces_zone_alias:
                            interfaces_zone_alias.remove(zalias)
                    else:
                        msg.add_error("Interface {iface} not removed from zone: {error}".format(iface=iface["interface_alias"], error=v.reason))


    # each interface set on form we need to add to zone
    for iface in interfaces_form:
        if iface in interfaces_zone:
            msg.add_info("Zone add interface {iface} not added since already addded.".format(iface=iface))
        elif iface in interfaces_zone_other:
            msg.add_alert("Zone add interface {iface} not added since belongs to other zone.".format(iface=iface))
        else:
            v = vapi.set_firewall_zone_interface(hostname_default, zonename, iface)
            if v.success:   
                valid = True
                msg.add_success("Zone add interface {iface} added.".format(iface=iface))
                zalias = "interface_" + iface
                interfaces_zone_alias.append(zalias)
            else:
                msg.add_success("Zone add interface {iface} not added: {error}.".format(iface=iface, error=v.reason))
    
    if request.POST.get('description', None) != None:
        zonedescription = request.POST.get('description')
        zonedescription = zonedescription.strip()
        if 'description' not in zoneinfo or zoneinfo['description'] != zonedescription:
            if len(zonedescription) > 0:
                v = vapi.set_firewall_zone_description(hostname_default, zonename, zonedescription)
                if v.success:   
                    valid = True
                    msg.add_success("Description defined")
                    zoneinfo['description'] = zonedescription
                else:
                    msg.add_success("Description failed to set")

    if request.POST.get('action', None) != None:
        zoneaction = request.POST.get('action')
        zoneaction = zoneaction.strip()
        if zoneaction in ['drop', 'reject']:
            if 'default-action' not in zoneinfo or zoneinfo['default-action'] != zoneaction:
                v = vapi.set_firewall_zone_defaultaction(hostname_default, zonename, zoneaction)
                if v.success:   
                    valid = True
                    msg.add_success("Default action defined")     
                    zoneinfo['default-action'] = zoneaction  
                else:
                    msg.add_success("Default action failed to set")                        


    """if request.POST.get('localzone', None) != None:
            # set local-zone
            v = vapi.set_firewall_zone_localzone(hostname_default, zonename)
            if v.success:   
                valid = True
                msg.add_success("Local-zone defined")       
            else:
                msg.add_success("Local-zone failed to set")"""

    zoneaction = None
    if 'default-action' in zoneinfo:
        zoneaction = zoneinfo['default-action']

    template = loader.get_template('firewall/zones-edit.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                        all_instances,
        'hostname_default':                 hostname_default,
        'username':                         request.user,
        'is_superuser':                     is_superuser,
        'interfaces':                       interfaces,
        'interfaces_pretty':                pprint.pformat(interfaces, indent=4, width=120),
        'interfaces_all_names_pretty':      pprint.pformat(interfaces_all_names, indent=4, width=120),
        'interfaces_all_names':             interfaces_all_names,
        'msg' :                             msg.get_all(),
        'allzones':                         allzones,
        'interfaces_defined':               interfaces_defined,
        'interfaces_defined_form':          interfaces_defined_form,
        'interfaces_zone_alias':            interfaces_zone_alias,
        'interfaces_zone_alias_other':      interfaces_zone_alias_other,
        "zoneinfo":                         zoneinfo,
        "allzones_pretty":                  pprint.pformat(allzones, indent=4, width=120),
        "zonename":                         zonename,
        "exists":                           True,
        'interfaces_all_names_dict':        interfaces_all_names_dict,
        'interfaces_all_names_dict_pretty': pprint.pformat(interfaces_all_names_dict, indent=4, width=120),
        'zoneaction':                       zoneaction,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_zones_remove(request, zonename):
    # validation
    zonename = zonename.strip()
    
    msg = vmsg.msg()
    
    # basic methods all views should call
    all_instances       = vyos.instance_getall()
    hostname_default    = vyos.get_hostname_prefered(request)
    is_superuser        = perms.get_is_superuser(request.user)

    # local methods to prepare env
    interfaces              = vyos.get_interfaces(hostname_default)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)
    get_firewall_zone       = vapi.get_firewall_zone(hostname_default, zonename)
    zoneinfo                = get_firewall_zone.data

    if zoneinfo == None:
        msg.add_error("Zone not exists")
    else:
        v = vapi.delete_firewall_zone(hostname_default, zonename)
        if v.success:   
            msg.add_success("Zone {zone} removed".format(zone=zonename))
        else:
            msg.add_error("Zone {zone} not removed: {error}".format(zone=zonename, error=v.reason))

    template = loader.get_template('firewall/zones-remove.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                    all_instances,
        'hostname_default':             hostname_default,
        'username':                     request.user,
        'is_superuser':                 is_superuser,
        'interfaces':                   interfaces,
        'interfaces_all_names_pretty':  pprint.pformat(interfaces_all_names, indent=4, width=120),
        'interfaces_all_names':         interfaces_all_names,
        'msg' :                         msg.get_all(),
        "zoneinfo":                     zoneinfo,
        "zonename":                     zonename,
    }   
    return HttpResponse(template.render(context, request))

@is_authenticated
def firewall_zones_addrule(request):
    msg = vmsg.msg()
    
    # basic methods all views should call
    all_instances       = vyos.instance_getall()
    hostname_default    = vyos.get_hostname_prefered(request)
    is_superuser        = perms.get_is_superuser(request.user)

    # local methods to prepare env
    interfaces              = vyos.get_interfaces(hostname_default)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)
    get_firewall_zones      = vapi.get_firewall_zones(hostname_default) 

    zones = []
    if get_firewall_zones.success:
        allzones = get_firewall_zones.data
        if 'zone' in allzones:
            for zone in allzones['zone']:
                zones.append(zone)                        

    firewalls = []
    firewall_all = vyos.get_firewall_all(hostname_default)
    if firewall_all == False:
        return redirect('firewall:firewall-create')
    if 'name' in firewall_all:
        for firewall in firewall_all['name']:
            firewalls.append(firewall)

    reverse = False
    if request.POST.get('reverse', None) == "1":
        reverse = True

    dstzone = None
    srczone = None
    firewallrule = None

    if request.POST.get('dstzone', None) != None:
        dstzone = request.POST.get('dstzone').strip()

    if request.POST.get('srczone', None) != None:
        srczone = request.POST.get('srczone').strip()

    if request.POST.get('firewall', None) != None:
        firewallrule = request.POST.get('firewall').strip()

    if dstzone != None and srczone != None and firewallrule != None:
        v = vapi.set_interface_firewall_zone_addrule(hostname_default, dstzone, srczone, firewallrule)
        if v.success:   
            msg.add_success("Zone ruleset zone {dst} from {src} firewall {firewall} added".format(
                dst=dstzone,
                src=srczone,
                firewall=firewallrule
            ))
        else:
            msg.add_error("Zone ruleset {dst} from {src} firewall {firewall} not added: {reason}".format(
                dst=dstzone,
                src=srczone,
                firewall=firewallrule
            ))

        if reverse == True:
            v = vapi.set_interface_firewall_zone_addrule(hostname_default, srczone, dstzone, firewallrule)
            if v.success:   
                msg.add_success("Zone reverse ruleset {dst} from {src} firewall {firewall} added".format(
                    dst=srczone,
                    src=dstzone,
                    firewall=firewallrule
                ))
            else:
                msg.add_error("Zone reverse ruleset {dst} from {src} firewall {firewall} not added: {reason}".format(  
                    dst=srczone,
                    src=dstzone,
                    firewall=firewallrule
                ))



 
    template = loader.get_template('firewall/zones-addrule.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                    all_instances,
        'hostname_default':             hostname_default,
        'username':                     request.user,
        'is_superuser':                 is_superuser,
        'interfaces':                   interfaces,
        'interfaces_all_names_pretty':  pprint.pformat(interfaces_all_names, indent=4, width=120),
        'interfaces_all_names':         interfaces_all_names,
        'msg' :                         msg.get_all(),
        'zones' :                       zones,
        'firewalls' :                   firewalls
    }   
    return HttpResponse(template.render(context, request))



@is_authenticated
def firewall_zones_removerule(request, dstzone, srczone, firewall):
    # validation
    dstzone = dstzone.strip()
    srczone = srczone.strip()
    firewall = firewall.strip()
    
    msg = vmsg.msg()
    
    # basic methods all views should call
    all_instances       = vyos.instance_getall()
    hostname_default    = vyos.get_hostname_prefered(request)
    is_superuser        = perms.get_is_superuser(request.user)

    # local methods to prepare env
    interfaces              = vyos.get_interfaces(hostname_default)
    interfaces_all_names    = vyos.get_interfaces_all_names(hostname_default)
    get_firewall_zonedst    = vapi.get_firewall_zone(hostname_default, dstzone)
    zoneinfodst             = get_firewall_zonedst.data
    get_firewall_zonesrc    = vapi.get_firewall_zone(hostname_default, srczone)
    zoneinfosrc             = get_firewall_zonesrc.data    

    if zoneinfodst == None or zoneinfosrc == None:
        msg.add_error("Zone not exists")
    else:
        v = vapi.delete_interface_firewall_zone_rule(hostname_default, dstzone, srczone)
        if v.success:   
            msg.add_success("Zone ruleset {dst} from {src} removed".format(  
                dst=dstzone,
                src=srczone,
            ))            
        else:
            msg.add_error("Zone ruleset {dst} from {src} not removed: {reason}".format(  
                dst=dstzone,
                src=srczone,
                reason=v.reason
            ))

    template = loader.get_template('firewall/zones-removerule.html')
    context = { 
        #'interfaces': interfaces,
        'instances':                    all_instances,
        'hostname_default':             hostname_default,
        'username':                     request.user,
        'is_superuser':                 is_superuser,
        'interfaces':                   interfaces,
        'interfaces_all_names_pretty':  pprint.pformat(interfaces_all_names, indent=4, width=120),
        'interfaces_all_names':         interfaces_all_names,
        'msg' :                         msg.get_all(),
    }   
    return HttpResponse(template.render(context, request))