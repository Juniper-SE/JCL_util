#!/usr/bin/python3

import csv
import ipaddress
from pprint import pprint
from collections import defaultdict



ipv6_subnet = "2001:192:168:0::/56"
ipv6_p2p_prefix_length = 64

ipv4_subnet = "192.168.0.0/24"
ipv4_p2p_prefix_length = 30
############



if __name__ == "__main__":


    for ipv4_p2p_subnet,ipv6_p2p_subnet in zip(
            ipaddress.ip_network(ipv4_subnet).subnets(new_prefix=ipv4_p2p_prefix_length),
            ipaddress.ip_network(ipv6_subnet).subnets(new_prefix=ipv6_p2p_prefix_length)
            ):


       print ("")
       print (ipv4_p2p_subnet," ",ipv6_p2p_subnet)

       for ipv4_host, ipv6_host in zip (ipv4_p2p_subnet.hosts(),ipv6_p2p_subnet.hosts()):
           print ("\t",ipv4_host," ",ipv6_host)
           print ("\t",ipv4_host,"\t set interface   unit 0 family inet address",ipv4_host)
           print ("\t",ipv6_host,"\t set interface   unit 0 family inet6 address",ipv6_host)




