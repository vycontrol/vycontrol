import sys
import socket
import pprint
import re

def get_protocols():
    file = '/etc/protocols'
    
    protocols = {}
    # Iterate through the file, one line at a time
    for line in open(file):
        line = line.replace("'","")
        line = line.replace('"',"")
        if line[0:1] != '#' and not line.isspace():
            linesplited = re.split(r'([\t\s]+)', line, maxsplit=2)
            #pprint.pprint(linesplited)
            protocol_name = linesplited[0].strip()
            protocol_id = linesplited[2].strip()
            protocols[protocol_id] = protocol_name
            #print(linesplited[0], linesplited[2])

    #pprint.pprint(protocols)

    inv_map = {v: k for k, v in protocols.items()}

    common = ['tcp', 'udp', 'icmp', 'gre', 'ospf', 'igmp', 'egp', 'igp', 'ipv6', 'ip', 'isis']

    return {'all_by_id': protocols, 'all_by_name': inv_map, 'common': common}

def get_services():
    # set the file name depending on the operating system
    if sys.platform == 'win32':
        file = r'C:\WINDOWS\system32\drivers\etc\services'
    else:
        file = '/etc/services'

    def is_number(s):
        try:
            complex(s) # for int, long, float and complex
        except ValueError:
            return False

        return True


    protocols = []
    service_name = {}
    portprotocol = {}

    # Iterate through the file, one line at a time
    for line in open(file):
        line = line.replace("'","")
        line = line.replace('"',"")



        if line[0:1] != '#' and not line.isspace():
            #pprint.pprint(line.strip())


            linesplited = re.split(r'([\t\s]+)', line, maxsplit=2)
            linesplited_clean = {}
            #pprint.pprint(linesplited)
            x = 0
            service_name_actual = None
            for line_clean in linesplited:
                line_clean = re.sub('#', '', line_clean.strip())
                line_clean_strip = re.sub(r'\s+', '', line_clean)

                if x == 0 and line_clean_strip == "":
                    linesplited_clean['service_name'] = None
                elif x == 0 and is_number(line_clean_strip) == False: 
                    linesplited_clean['service_name'] = line_clean_strip
                    service_name_actual = line_clean_strip
                    service_name[line_clean_strip] = {}

                    #print('isnumberfalse', is_number(line_clean_strip), line_clean_strip)
                elif x == 2 and len(line_clean_strip) > 0:
                    linesplited_clean['port_protocol'] = line_clean_strip
                    
                    portprotocol = line_clean_strip.split('/')
                    linesplited_clean['port'] = portprotocol[0]
                    linesplited_clean['protocol'] = portprotocol[1]

                    if str(portprotocol[1]) not in protocols:
                        protocols.append(str(portprotocol[1]))

                    if service_name_actual != None:
                        service_name[service_name_actual]['p'] = str(portprotocol[1])
                        service_name[service_name_actual]['n'] = str(portprotocol[0])

                elif x == 4 and len(line_clean_strip) > 0:
                    linesplited_clean['description'] = line_clean_strip
                    if service_name_actual != None:
                        service_name[service_name_actual]['d'] = line_clean_strip

                #re.sub('#', '', line_clean_strip)

                x = x + 1
            #pprint.pprint(linesplited_clean)
            #print("#####################")

    common = {
        'http' : 'http',
        'https' : 'https',
        'ftp' : 'ftp',
        'ftp-data' : 'ftp-data',
        'ssh' : 'ssh',
        'telnet' : 'telnet',
        'smtp' : 'smtp', 
        'nicname' : 'whois',
        'domain' : 'dns',
        'pop3' : 'pop3',
        'sftp' : 'sftp',
        'ntp' : 'ntp',
        'snmp' : 'snmp',
        'snmptrap' : 'snmptrap',
        'bgp' : 'bgp',
        'imaps' : 'imaps',
        'pop3s' : 'pop3s',
        'ftps-data' : 'ftps-data',
        'ftps' : 'ftps',
        'pop3s' : 'pop3s',
    }

    return {'protocols': protocols, 'services': service_name, 'common': common}

