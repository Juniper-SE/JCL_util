#!/usr/bin/python3

import yaml
import re
from pprint import pprint

with open("topology.yaml", "r") as stream:
    try:
        topo_data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

print ("topo = ")
pprint (topo_data)


for device, ports in topo_data['topo'].items():
     print ("\n")
     print ("device = ",device)
     #print ("ports = ",ports)
     for port_num,port_data in ports.items():
         print ("\n")
         print ("   ","port_num = ",port_num)
         print ("   ","port_data = ",port_data)
         print ("   ","port_data[name] = ",port_data['name'])
         print ("   ","port_data[peer] = ",port_data['peer'])
         print ("   ","port_data[pport] = ",port_data['pport'])
         print ("   ","peer = ",port_data["peer"])
         print ("   ","peer port = ",topo_data['topo'][port_data["peer"]][port_data['pport']]['name'])
         peer_device = port_data["peer"]
         peer_port = topo_data['topo'][port_data["peer"]][port_data['pport']]['name']
         print ("   ","(",device,",",port_data['name'],",",peer_device,",",peer_port,")")
         #print ("   ","peer = ",topo_data['topo'][port_data["peer"]][port_data['pport']]['name'])




#for device, ports in topo_data['topo'].items():
#     print("\n",device, '->', ports)
#     if not(re.search(r'^vMX', device)):
#         print ("Skip ",device)
#         continue
#     for port in ports:
#         print ("PORT = ",port)
#         #print ("   ",ports[port])
#         if not(re.search(r'^vMX',ports[port]["peer"])):
#             print ("Skip peer ",ports[port]["peer"])
#             continue
#         print ("Process ",ports[port])



