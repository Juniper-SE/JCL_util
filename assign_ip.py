#!/usr/bin/python3

import yaml
import re
from pprint import pprint

with open("topology.yaml", "r") as stream:
    try:
        topo_data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

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



if __name__ == "__main__":
    edge_list = get_edge_list(topo_data)
    pprint (edge_list)

