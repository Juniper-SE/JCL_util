#!/usr/bin/python3

import yaml
import re
import argparse
from pprint import pprint

#print ("topo = ")
#pprint (topo_data)

def get_edge_list(topo_data):
    edge_list = []
    for device, ports in topo_data['topo'].items():
        #print ("\n")
        #print ("device = ",device)
        for port_num,port_data in ports.items():
            #print ("\n")
            #print ("   ","port_num = ",port_num)
            #print ("   ","port_data = ",port_data)
            #print ("   ","port_data[name] = ",port_data['name'])
            #print ("   ","port_data[peer] = ",port_data['peer'])
            #print ("   ","port_data[pport] = ",port_data['pport'])
            #print ("   ","peer = ",port_data["peer"])
            #print ("   ","peer port = ",topo_data['topo'][port_data["peer"]][port_data['pport']]['name'])
            peer_device = port_data["peer"]
            peer_port = topo_data['topo'][port_data["peer"]][port_data['pport']]['name']
            #print ("   ","(",device,",",port_data['name'],",",peer_device,",",peer_port,")")
            #print ("   ","peer = ",topo_data['topo'][port_data["peer"]][port_data['pport']]['name'])
            edge_list.append([device,port_data['name'],peer_device,peer_port])
    return edge_list


def remove_dup_edges(edge_list):
    uniq_edge_list = []
    for edge in edge_list:
        reverse_edge = [edge[2],edge[3],edge[0],edge[1]]
        if edge not in uniq_edge_list and reverse_edge not in uniq_edge_list:
            uniq_edge_list.append(edge)
    return (uniq_edge_list)



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
    pprint (edge_list)
    uniq_edge_list = remove_dup_edges(edge_list)
    pprint (uniq_edge_list)

