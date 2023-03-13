#!/usr/bin/python3

import csv
import ipaddress
from pprint import pprint
from collections import defaultdict



ipv6_subnet = "2001:10:10:0::/64"
ipv6_p2p_prefix_length = 128

ipv4_subnet = "10.0.0.0/24"
ipv4_p2p_prefix_length = 32
############



if __name__ == "__main__":

    #ipv6_list = list(ipaddress.ip_network(ipv6_subnet).subnets(new_prefix=ipv6_p2p_prefix_length))
    #ipv4_list = list(ipaddress.ip_network(ipv4_subnet).subnets(new_prefix=ipv4_p2p_prefix_length))

    for ipv4,ipv6 in zip(
            ipaddress.ip_network(ipv4_subnet).subnets(new_prefix=ipv4_p2p_prefix_length),
            ipaddress.ip_network(ipv6_subnet).subnets(new_prefix=ipv6_p2p_prefix_length)
            ):
        print ("")
        print (ipv4,"\t",ipv6)
        print (ipv4,"\tset interface lo0.0 family inet address",ipv4)
        print (ipv6,"\tset interface lo0.0 family inet6 address",ipv6)

