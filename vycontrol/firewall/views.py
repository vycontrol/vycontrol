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
import vycontrol_messages as vcmsg


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


    firewall2 = vapilib.api(
        hostname =      hostname_default,
        api =           'get',
        op =            'showConfig',
        cmd =           {"op": "showConfig", "path": ["firewall"]},
        description =   "get all firewall",
    )



    is_superuser = perms.get_is_superuser(request.user)



    firewall_all = vyos.get_firewall_all(hostname_default)
    if firewall_all == False:
        return redirect('firewall:firewall-create')

    for xitem in firewall_all['name']:
        if 'default-action' in firewall_all['name'][xitem]:
            firewall_all['name'][xitem]['default_action'] = firewall_all['name'][xitem]['default-action']
            del firewall_all['name'][xitem]['default-action']

    template = loader.get_template('firewall/list.html')
    context = { 
        #'interfaces': interfaces,
        'instances': all_instances,
        'hostname_default': hostname_default,
        'firewall_all':  firewall_all,
        'username': request.user,
        'is_superuser' : is_superuser,
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


def changerule(request, firewall_name, mode, template_name="firewall/addrule.html", rulenumber = None):
    msg = vcmsg.msg()

    #interfaces = vyos.get_interfaces()
    all_instances = vyos.instance_getall()
    hostname_default = vyos.get_hostname_prefered(request)
    is_superuser = perms.get_is_superuser(request.user)

    # get all selected firewall data  --- WHY NEED ALL FIREWALL???? 
    firewall = vyos.get_firewall(hostname_default, firewall_name)




    # get all firewall groups
    firewall_group = {}
    firewall_group['network-group'] = {}
    firewall_group['address-group'] = {}
    firewall_group['port-group'] = {}
    firewall_group_raw = vapi.get_firewall_group(hostname_default)
    if firewall_group_raw.success:
        if 'network-group' in firewall_group_raw.data:
            for g in firewall_group_raw.data['network-group']:
                firewall_group['network-group'][g] = firewall_group_raw.data['network-group'][g]

        if 'address-group' in firewall_group_raw.data:
            for g in firewall_group_raw.data['address-group']:
                firewall_group['address-group'][g] = firewall_group_raw.data['address-group'][g]

        if 'port-group' in firewall_group_raw.data:
            for g in firewall_group_raw.data['port-group']:
                firewall_group['port-group'][g] = firewall_group_raw.data['port-group'][g]
    firewall_networkgroup_js = json.dumps(firewall_group['network-group'])
    firewall_addressgroup_js = json.dumps(firewall_group['address-group'])


    netservices = network.get_services()
    netservices_js = json.dumps(netservices)
    portgroups = vyos.get_firewall_portgroup(hostname_default)

    

    if portgroups != False:
        portgroups_groups = portgroups['port-group']
    else:
        portgroups_groups = []

    changed = False
    rulenumber_valid = False
    ruleaction_valid = False
    ruledata = {}


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
                ruleaction_valid = True
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
    # update criteria_protocol
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
    else:
        msg.add_info("Criteria Ports Destination: no changes")

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
    else:
        msg.add_info("Criteria Ports Source: no changes")
    

    # if criteria_tcpflags set, save it
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
                changed = True 

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
                changed = True 

                #if 'source' in ruledata and 'port' in ruledata['source']:
                #    del ruledata['source']['port']
                if 'tcp' not in ruledata:
                    ruledata['tcp'] = {}
                ruledata['tcp']['flags'] = ",".join(tcpflags_form)
            else:
                msg.add_error("Criteria TCP Ports: updated failed - " + v.reason)







    if rulenumber_valid == True:
        if False:
            # verifing basic informations, should have rulenumber, status and ruleaction
            msg.add_error("Invalid Status or Action")
        elif False:
            # rule created, continue to configure firewall rule according his criterias
            if v.success:
                

                
                    

                # if criteria_address set, save it
                if request.POST.get('criteria_address', None) == "1":
                    # negate sdaddress_source
                    if request.POST.get('sdaddress_source_negate', None) == "1":
                        sdaddress_source_negate = "!"
                    else:
                        sdaddress_source_negate = ""

                    # negate sdaddress_destination_negate
                    if request.POST.get('sdaddress_destination_negate', None) == "1":
                        sdaddress_destination_negate = "!"
                    else:
                        sdaddress_destination_negate = ""                    


                    if request.POST.get('sdaddress_source', None) != None:              
                        sdaddress_source = request.POST.get('sdaddress_source')
                        sdaddress_source_txt = sdaddress_source_negate + sdaddress_source
                        
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "address", sdaddress_source_txt],
                            description = "set sdaddress_source",
                        )
                        if v.success:
                            changed = True 


                    if request.POST.get('sdaddress_destination', None) != None:              
                        sdaddress_destination = request.POST.get('sdaddress_destination')                    
                        sdaddress_destination_txt = sdaddress_destination_negate + sdaddress_destination

                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "address", sdaddress_destination_txt],
                            description = "set sdaddress_destination_txt",
                        )
                        if v.success:
                            changed = True 

                # if criteria_addressgroup set, save it
                if request.POST.get('criteria_addressgroup', None) == "1":
                    if request.POST.get('sdaddressgroup_source', None) != None:              
                        sdaddressgroup_source = request.POST.get('sdaddressgroup_source')
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "address-group", sdaddressgroup_source],
                            description = "set sdaddressgroup_source",
                        )
                        vcmsg.log("set sdaddressgroup_source", v.data)

                        if v.success:
                            changed = True 

                    if request.POST.get('sdaddressgroup_destination', None) != None:              
                        sdaddressgroup_destination = request.POST.get('sdaddressgroup_destination')                    
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "address-group", sdaddressgroup_destination],
                            description = "set sdaddressgroup_destination",
                        )
                        vcmsg.log("set sdaddressgroup_destination", v.data)

                        if v.success:
                            changed = True 

                # if criteria_networkgroup set, save it
                if request.POST.get('criteria_networkgroup', None) == "1":
                    if request.POST.get('sdnetworkgroup_source', None) != None:              
                        sdnetworkgroup_source = request.POST.get('sdnetworkgroup_source')
                        v = vapilib.api (
                                hostname=   hostname_default,
                                api =       "post",
                                op =        "set",
                                cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "network-group", sdnetworkgroup_source],
                                description = "set sdnetworkgroup_source",
                        )
                        if v.success:
                            changed = True 
                        else:
                            vcmsg.log("sdnetworkgroup_source", v.error)

                    if request.POST.get('sdnetworkgroup_destination', None) != None:              
                        sdnetworkgroup_destination = request.POST.get('sdnetworkgroup_destination')                    
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "network-group", sdnetworkgroup_destination],
                            description = "set sdnetworkgroup_destination",
                        ) 
                        if v.success:
                            changed = True                  
                        else:
                            vcmsg.log("sdnetworkgroup_source", v.error)                        

                # if criteria_sourcemac set, save it
                if request.POST.get('criteria_sourcemac', None) == "1":
                    # negate sdaddress_source
                    if request.POST.get('smac_source_negate', None) == "1":
                        sourcemac_negate = "!"
                    else:
                        sourcemac_negate = ""               
        
                    if request.POST.get('smac_source', None) != None:
                        sourcemac = request.POST.get('smac_source')
                        sourcemac = sourcemac.replace("-",":")
                        sourcemac = sourcemac.lower()

                        sourcemac_txt = sourcemac_negate + sourcemac

                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "mac-address", sourcemac_txt],
                            description = "set source mac",
                        )
                        if v.success:
                            changed = True 

                # if criteria_packetstate set, save it
                if request.POST.get('criteria_packetstate', None) == "1":
                    packetstates = []
                    if request.POST.get('packetstate_established', None) == "1":
                        packetstates.append('established')
                    if request.POST.get('packetstate_invalid', None) == "1":
                        packetstates.append('invalid')
                    if request.POST.get('packetstate_new', None) == "1":
                        packetstates.append('new')
                    if request.POST.get('packetstate_related', None) == "1":
                        packetstates.append('related')

                    if len(packetstates) > 0:
                        for packetstate in packetstates:
                            v = vapilib.api (
                                hostname=   hostname_default,
                                api =       "post",
                                op =        "set",
                                cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "state", packetstate, "enable"],
                                description = "set criteria_packetstate",
                            )
                            if v.success:
                                changed = True

                

                # if criteria_portgroup set, save it
                if request.POST.get('criteria_portgroup', None) == "1":
                    if request.POST.get('sdportgroup_source', None) != None:
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "source", "group", "port-group", request.POST.get('sdportgroup_source')],
                            description = "set sdportgroup_source",
                        )
                        if v.success:
                            changed = True

                    if request.POST.get('sdportgroup_destination', None) != None:
                        v = vapilib.api (
                            hostname=   hostname_default,
                            api =       "post",
                            op =        "set",
                            cmd =       ["firewall", "name", firewall_name, "rule", rulenumber, "destination", "group", "port-group", request.POST.get('sdportgroup_destination')],
                            description = "set sdportgroup_destination",
                        )
                        if v.success:
                            changed = True                        

    if changed == True:
        msg.add_success("Firewall rule saved")
        

    ruledata_json = json.dumps(ruledata)
    vcmsg.log("json", ruledata_json)


    template = loader.get_template(template_name)
    context = { 
        #'interfaces': interfaces,
        'instances':                        all_instances,
        'hostname_default':                 hostname_default,
        'firewall':                         firewall,
        'firewall_name':                    firewall_name,
        'username':                         request.user,
        'is_superuser' :                    is_superuser,
        'services' :                        netservices['services'],
        'services_common' :                 netservices['common'],
        'firewall_networkgroup':            firewall_group['network-group'],
        'firewall_addressgroup':            firewall_group['address-group'],
        'firewall_networkgroup_js':         firewall_networkgroup_js,
        'firewall_addressgroup_js':         firewall_addressgroup_js,
        'netservices_js' :                  netservices_js,
        'portgroups_groups':                portgroups_groups,
        'mode' :                            mode,
        'msg' :                             msg.get_all(),
        'ruledata' :                        ruledata,
        'ruledata_pretty' :                 pprint.pformat(ruledata, indent=4, width=120),
        'ruledata_json' :                   ruledata_json,
        'rulenumber' :                      rulenumber,
    }

    if mode == "editrule":
        pass

    return HttpResponse(template.render(context, request))
    
@is_authenticated
def addrule(request, firewall_name):
    return changerule(request, firewall_name, mode="addrule", template_name="firewall/editrule.html", rulenumber = None)

@is_authenticated
def editrule(request, firewall_name, rulenumber):
    return changerule(request, firewall_name, mode="editrule", template_name="firewall/editrule.html", rulenumber=rulenumber)

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

        vcmsg.log('networks', networks)

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

        vcmsg.log('networks', networks)

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
            vcmsg.log("tipo", type(networks_original))
            networks_original = [groupinfo['address']]
        else:
            networks_original = groupinfo['address']

    vcmsg.log("networks_original", networks_original)

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

            vcmsg.log('networks new', networks_new)

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
            
            vcmsg.log('networks original', networks_original)

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
            vcmsg.log("tipo", type(networks_original))
            networks_original = [groupinfo['network']]
        else:
            networks_original = groupinfo['network']

    vcmsg.log("networks_original", networks_original)

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

            vcmsg.log('networks new', networks_new)

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
            
            vcmsg.log('networks original', networks_original)

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