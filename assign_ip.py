#!/usr/bin/python3

import yaml
import re
import argparse
import ipaddress
from pprint import pprint

#print ("topo = ")
#pprint (topo_data)

def get_edge_list(topo_data):
    edge_list = []
    for device, ports in topo_data['topo'].items():
        for port_num,port_data in ports.items():
            peer_device = port_data["peer"]
            peer_port = topo_data['topo'][port_data["peer"]][port_data['pport']]['name']
            edge_list.append([device,port_data['name'],peer_device,peer_port])
    return edge_list


def remove_dup_edges(edge_list):
    uniq_edge_list = []
    for edge in edge_list:
        reverse_edge = [edge[2],edge[3],edge[0],edge[1]]
        if edge not in uniq_edge_list and reverse_edge not in uniq_edge_list:
            uniq_edge_list.append(edge)
    return (uniq_edge_list)

def remove_non_jnpr(edge_list):
    jnpr_edge_list = []
    jnpr = r'^v((MX)|(PTX))'
    
    for edge in edge_list:
        if not(re.search(jnpr, edge[0])) or not(re.search(jnpr,edge[2])):
            continue
        jnpr_edge_list.append(edge)
    return jnpr_edge_list

def assign_ip(edge_list):

    ipv4_address = iter( ipaddress.ip_network(args.ipv4_subnet).subnets(new_prefix=ipv4_p2p_prefix_length))
    ipv6_address = iter( ipaddress.ip_network(args.ipv6_subnet).subnets(new_prefix=ipv6_p2p_prefix_length))

    for edge in edge_list:
        print ("\n")
        print (edge)
        ipv4_ptp_subnet = next(ipv4_address)
        ipv6_ptp_subnet = next(ipv6_address)
        print ("ipv4_ptp_subnet = ",ipv4_ptp_subnet)
        print ("ipv6_ptp_subnet = ",ipv6_ptp_subnet)
        ipv4_host = iter(ipv4_ptp_subnet.hosts())
        ipv6_host = iter(ipv6_ptp_subnet.hosts())
        #ipv4_addr_1 = next(ipv4_ptp_subnet.hosts())
        #ipv6_addr_1 = next(ipv6_ptp_subnet.hosts())
        #ipv4_addr_2 = next(ipv4_ptp_subnet.hosts())
        #ipv6_addr_2 = next(ipv6_ptp_subnet.hosts())
        print (edge[0],edge[1],next(ipv4_host),next(ipv6_host))
        print (edge[2],edge[3],next(ipv4_host),next(ipv6_host))

        



#    for ipv4_p2p_subnet,ipv6_p2p_subnet in zip(
#            ipaddress.ip_network(ipv4_subnet).subnets(new_prefix=ipv4_p2p_prefix_length),
#            ipaddress.ip_network(ipv6_subnet).subnets(new_prefix=ipv6_p2p_prefix_length)
#            ):
#
#
#       print ("")
#       print (ipv4_p2p_subnet," ",ipv6_p2p_subnet)
#
#       for ipv4_host, ipv6_host in zip (ipv4_p2p_subnet.hosts(),ipv6_p2p_subnet.hosts()):
#           print ("\t",ipv4_host," ",ipv6_host)
#           print ("\t",ipv4_host,"\t set interface   unit 0 family inet address",ipv4_host)
#           print ("\t",ipv6_host,"\t set interface   unit 0 family inet6 address",ipv6_host)









if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Assign P2P addresses')
    parser.add_argument('--ipv4_subnet', default="192.168.0.0/24", help='IPv4 address range')
    parser.add_argument('--ipv6_subnet', default="2001:192:168:0::/56", help='IPv6 address range')
    parser.add_argument('topo_file', default="topology.yaml", help='JCL topology file')
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
    pprint (router_interfaces)



