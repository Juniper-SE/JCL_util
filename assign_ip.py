#!/usr/bin/python3

import yaml
import re
import argparse
import ipaddress
from pprint import pprint
from jinja2 import Template
from jnpr.junos import Device
from jnpr.junos.utils.config import Config


# https://readthedocs.org/projects/junos-pyez/




##########
def get_edge_list(topo_data):
    edge_list = []
    for device, ports in topo_data['topo'].items():
        for port_num,port_data in ports.items():
            peer_device = port_data["peer"]
            peer_port = topo_data['topo'][port_data["peer"]][port_data['pport']]['name']
            edge_list.append([device,port_data['name'],peer_device,peer_port])
    return edge_list


##########
def remove_dup_edges(edge_list):
    uniq_edge_list = []
    for edge in edge_list:
        reverse_edge = [edge[2],edge[3],edge[0],edge[1]]
        if edge not in uniq_edge_list and reverse_edge not in uniq_edge_list:
            uniq_edge_list.append(edge)
    return (uniq_edge_list)

##########
def remove_non_jnpr(edge_list):
    jnpr_edge_list = []
    jnpr = r'^v((MX)|(PTX))'
    
    for edge in edge_list:
        if not(re.search(jnpr, edge[0])) or not(re.search(jnpr,edge[2])):
            continue
        jnpr_edge_list.append(edge)
    return jnpr_edge_list

##########
def assign_ip(edge_list):
    device_configs = {}

    ipv4_address = iter(ipaddress.ip_network(args.ipv4_p2p_subnet).subnets(new_prefix=ipv4_p2p_prefix_length))
    ipv6_address = iter(ipaddress.ip_network(args.ipv6_p2p_subnet).subnets(new_prefix=ipv6_p2p_prefix_length))

    for edge in edge_list:
        #print ("\n")
        #print (edge)
        ipv4_ptp_subnet = next(ipv4_address)
        ipv6_ptp_subnet = next(ipv6_address)
        #print ("ipv4_ptp_subnet = ",ipv4_ptp_subnet)
        #print ("ipv6_ptp_subnet = ",ipv6_ptp_subnet)
        ipv4_host = iter(ipv4_ptp_subnet.hosts())
        ipv6_host = iter(ipv6_ptp_subnet.hosts())

        # Assign individual addresses
        ipv4_1 = str(next(ipv4_host)) + "/30"
        ipv6_1 = str(next(ipv6_host)) + "/64"
        ipv4_2 = str(next(ipv4_host)) + "/30"
        ipv6_2 = str(next(ipv6_host)) + "/64"


        # There has to be a better way to do this...
        if edge[0] in device_configs:
            device_configs[edge[0]].append(  {"interface":edge[1], "ipv4_address":ipv4_1, "ipv6_address":ipv6_1, "description": edge[2] + ":" + edge[3]} )
        else:
            device_configs[edge[0]] = [ {"interface":edge[1], "ipv4_address":ipv4_1, "ipv6_address":ipv6_1, "description": edge[2] + ":" + edge[3]} ]

        if edge[2] in device_configs:
            device_configs[edge[2]].append(  {"interface":edge[3], "ipv4_address":ipv4_2, "ipv6_address":ipv6_2, "description":edge[0]+":"+edge[1]} )
        else:
            device_configs[edge[2]] = [ {"interface":edge[3], "ipv4_address":ipv4_2, "ipv6_address":ipv6_2, "description":edge[0]+":"+edge[1]} ]

    ## Add lo0 interfaces
    ipv4_lo_address = iter(ipaddress.ip_network(args.ipv4_lo_subnet).subnets(new_prefix=32))
    ipv6_lo_address = iter(ipaddress.ip_network(args.ipv6_lo_subnet).subnets(new_prefix=128))
    # Skip the 0 address
    next(ipv4_lo_address)
    next(ipv6_lo_address)
    for rtr in device_configs:
        ipv4_lo = next(ipv4_lo_address)
        ipv6_lo = next(ipv6_lo_address)
        iso_lo = '49.{:0>4}.{:0>4}.{:0>4}.{:0>4}.00'.format(str(ipv4_lo).split('.')[0],str(ipv4_lo).split('.')[1],str(ipv4_lo).split('.')[2],str(ipv4_lo).split('.')[3].split('/')[0],fill='0')
        #print ("===",rtr,str(ipv4_lo_address),str(ipv6_lo_address),iso_lo)
        #print ("iso = ",iso_lo)
        device_configs[rtr].append(  {"interface":"lo0", "ipv4_address":str(ipv4_lo), "ipv6_address":str(ipv6_lo),"iso_address":iso_lo } )


    return device_configs

##########
def generate_interface_configs(rtr,router_interfaces):

    template = """
    interfaces {
    {% for interface in interfaces %}
    {{ interface.interface }} {
        {% if interface.description is defined and interface.description|length -%}
        description {{interface.description}}
        {% endif -%}
        unit 0 {
            replace: family inet {
                address {{ interface.ipv4_address }};
            }
            {% if interface.iso_address is defined and interface.iso_address|length -%}
            replace: family iso {
                address {{ interface.iso_address }};
            }
            {% else -%}
            family iso;
            {% endif -%}
            replace: family inet6 {
                address {{ interface.ipv6_address }};
            }
        }
      }
    {% endfor %}
    }


    protocols {
        isis {
            {% for interface in interfaces %}
            interface {{ interface.interface }}.0 {
            level 2 metric 10;
            }
            {% endfor %}
        }
    }

    """

    #pprint (rtr)
    #pprint (router_interfaces)
    j2_template = Template(template)

    # must be a better way to do this
    data ={}
    data["interfaces"] = router_interfaces
    return j2_template.render(data)


##########
def install_configs(rtr,configs):
    print ("INSTALL")

    #dev = Device(host=rtr, user="jcluser", passwd="Juniper!1", port=22)
    #try:
    #    dev.open()
    #except ConnectionError as err:
    #    print ("Cannot connect to device: {0}".format(err))
    #    sys.exit(1)
    #except Exception as err:
    #    print (err)
    #    exit(1)
    #print (dev.facts)

    # https://junos-pyez.readthedocs.io/en/latest/jnpr.junos.utils.html?highlight=load#jnpr.junos.utils.config.Config.load
    dev = Device(host=rtr, user='jcluser', password='Juniper!1', port=22).open()
    with Config(dev, mode='private') as cu:  
        cu.load(configs, format='text')
        cu.pdiff()
        if cu.commit_check():
            cu.commit()
    dev.close()
        

##########
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Assign IP addresses to JCL devices',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ipv4_p2p_subnet', default="192.168.0.0/24", help='IPv4 address range')
    parser.add_argument('--ipv6_p2p_subnet', default="2001:192:168:0::/56", help='IPv6 address range')
    parser.add_argument('--ipv4_lo_subnet', default="10.255.255.0/24", help='IPv4 lo address range')
    parser.add_argument('--ipv6_lo_subnet', default="2001:255:255:0::/64", help='IPv4 lo address range')
    parser.add_argument('--install', action='store_true', help='Install to devices')
    parser.add_argument('topo_file', nargs='?', default="/etc/ansible/group_vars/all/topology.yaml", help='JCL topology file')
    args = parser.parse_args()

    ipv6_p2p_prefix_length = 64
    ipv4_p2p_prefix_length = 30


    #with open("topology.yaml", "r") as stream:
    with open(args.topo_file, "r") as stream:
        try:
            topo_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    edge_list = get_edge_list(topo_data)
    #pprint (edge_list)
    uniq_edge_list = remove_dup_edges(edge_list)
    #pprint (uniq_edge_list)
    jnpr_uniq_edge_list = remove_non_jnpr(uniq_edge_list)
    #pprint (jnpr_uniq_edge_list)
    router_interfaces = assign_ip(jnpr_uniq_edge_list)
    #pprint (router_interfaces)

    for rtr in router_interfaces:
        print ("===",rtr,"===")
        interface_config = generate_interface_configs(rtr,router_interfaces[rtr])
        print (interface_config)
        if (args.install):
            install_configs(rtr,interface_config)






