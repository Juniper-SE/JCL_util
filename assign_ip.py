#!/usr/bin/python3

import yaml
import re
import argparse
import ipaddress
import csv
from pprint import pprint
from jinja2 import Template
from jnpr.junos import Device
from jnpr.junos.utils.config import Config


# https://readthedocs.org/projects/junos-pyez/


class ae_Iterator:
    def __init__(self):
        self.device_counter = {}

    def __call__(self, device):
        if device not in self.device_counter:
            self.device_counter[device] = 0
        self.device_counter[device] += 1
        return f"ae{self.device_counter[device]}"


##########
def get_edge_list(topo_data):
    edge_list = []
    for device, ports in topo_data['topo'].items():
        for port_num, port_data in ports.items():
            peer_device = port_data["peer"]
            peer_port = topo_data['topo'][port_data["peer"]
                                          ][port_data['pport']]['name']
            edge_list.append(
                [device, port_data['name'], peer_device, peer_port])
    return edge_list


##########
def remove_dup_edges(edge_list):
    uniq_edge_list = []
    for edge in edge_list:
        reverse_edge = [edge[2], edge[3], edge[0], edge[1]]
        if edge not in uniq_edge_list and reverse_edge not in uniq_edge_list:
            uniq_edge_list.append(edge)
    return (uniq_edge_list)

##########


def remove_non_jnpr(edge_list):
    jnpr_edge_list = []
    jnpr = r'^v((MX)|(PTX))'

    for edge in edge_list:
        if not (re.search(jnpr, edge[0])) or not (re.search(jnpr, edge[2])):
            continue
        jnpr_edge_list.append(edge)
    return jnpr_edge_list

##########


def assign_ip(edge_list):
    device_configs = {}

    for edge in edge_list:
        # print ("\n")
        # print (edge)
        ipv4_ptp_subnet = next(ipv4_address)
        ipv6_ptp_subnet = next(ipv6_address)
        ipv4_host = iter(ipv4_ptp_subnet.hosts())
        ipv6_host = iter(ipv6_ptp_subnet.hosts())

        # Assign individual addresses
        ipv4_1 = str(next(ipv4_host)) + "/30"
        ipv6_1 = str(next(ipv6_host)) + "/64"
        ipv4_2 = str(next(ipv4_host)) + "/30"
        ipv6_2 = str(next(ipv6_host)) + "/64"

        # There has to be a better way to do this...
        if edge[0] in device_configs:
            device_configs[edge[0]].append(
                {"interface": edge[1], "ipv4_address": ipv4_1, "ipv6_address": ipv6_1, "description": edge[2] + ":" + edge[3]})
        else:
            device_configs[edge[0]] = [{"interface": edge[1], "ipv4_address": ipv4_1,
                                        "ipv6_address": ipv6_1, "description": edge[2] + ":" + edge[3]}]

        if edge[2] in device_configs:
            device_configs[edge[2]].append(
                {"interface": edge[3], "ipv4_address": ipv4_2, "ipv6_address": ipv6_2, "description": edge[0]+":"+edge[1]})
        else:
            device_configs[edge[2]] = [{"interface": edge[3], "ipv4_address": ipv4_2,
                                        "ipv6_address": ipv6_2, "description": edge[0]+":"+edge[1]}]

    for rtr in device_configs:
        ipv4_lo = next(ipv4_lo_address)
        ipv6_lo = next(ipv6_lo_address)
        iso_lo = '49.{:0>4}.{:0>4}.{:0>4}.{:0>4}.00'.format(str(ipv4_lo).split('.')[0], str(ipv4_lo).split(
            '.')[1], str(ipv4_lo).split('.')[2], str(ipv4_lo).split('.')[3].split('/')[0], fill='0')
        # print ("===",rtr,str(ipv4_lo_address),str(ipv6_lo_address),iso_lo)
        # print ("iso = ",iso_lo)
        device_configs[rtr].append({"interface": "lo0", "ipv4_address": str(
            ipv4_lo), "ipv6_address": str(ipv6_lo), "iso_address": iso_lo})

    return device_configs

##########
def generate_interface_configs(rtr, router_interfaces):

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
            family mpls;
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
        mpls {
            {% for interface in interfaces if not interface.interface=="lo0" %}
            interface {{ interface.interface }}.0 ;
            {% endfor %}
        }
        lldp {
            interface all;
        }

    }

    """

    print ("rtr = ",rtr)
    pprint (router_interfaces)
    j2_template = Template(template)

    # must be a better way to do this
    data = {}
    data["interfaces"] = router_interfaces
    return j2_template.render(data)

##########
def generate_lag_configs(rtr, lag_interfaces):

    template = """

interfaces {
    {% for key,value in lag.items() %}
      {% for int in lag[key].interfaces %}
        replace: {{int}} {
            description "{{lag[key].description}}";
            gigether-options {
               802.3ad {{key}};
            }
       }
      {% endfor %}
      replace: {{key}} {
          description "{{lag[key].description}}";
          unit 0 {
              family inet {
                  address {{lag[key].ipv4}}
              }
              family inet6 {
                  address {{lag[key].ipv6}}
              }
          }
      }
    {% endfor %}
}

    """

    #print ("lag rtr = ",rtr)
    #pprint (lag_interfaces)
    j2_template = Template(template)

    # must be a better way to do this
    data = {}
    #data["interfaces"] = router_interfaces
    config = j2_template.render({"lag":lag_interfaces})
    return config


##########
def install_configs(rtr, configs):
    print("INSTALL")

    # dev = Device(host=rtr, user="jcluser", passwd="Juniper!1", port=22)
    # try:
    #    dev.open()
    # except ConnectionError as err:
    #    print ("Cannot connect to device: {0}".format(err))
    #    sys.exit(1)
    # except Exception as err:
    #    print (err)
    #    exit(1)
    # print (dev.facts)

    # https://junos-pyez.readthedocs.io/en/latest/jnpr.junos.utils.html?highlight=load#jnpr.junos.utils.config.Config.load
    dev = Device(host=rtr, user='jcluser',
                 password='Juniper!1', port=22).open()
    with Config(dev, mode='private') as cu:
        cu.load(configs, format='text')
        cu.pdiff()
        if cu.commit_check():
            cu.commit()
    dev.close()

##########


def lag_interfaces(edge_list):
    """ Find lag interfaces """

    # print("LAG Interfaces")

    # print("=== edge_list ===")
    # pprint(edge_list)

    lag = []
    new_edge_list = []
    while edge_list:

        # Take each edge in edge_list
        edge = edge_list.pop()
        parallel_count = 0
        parallel_edge_list = []

        # Iterate over the list and look for other edges with the same device
        for x in range(len(edge_list)):
            try:
                # should we also look for "reverse" edges? - I think remove_dup edges handeled this
                if edge[0] == edge_list[x][0] and edge[2] == edge_list[x][2]:
                    parallel_count += 1
                    if parallel_count == 1:
                        parallel_edge_list.append(edge)
                    parallel_edge = edge_list.pop(x)
                    parallel_edge_list.append(parallel_edge)
            except IndexError:  # Should not modify the list we are iterating over.
                pass
        if parallel_count == 0:
            new_edge_list.append(edge)
        else:
            lag.append(parallel_edge_list)

    # print("=== new_edge_list ===")
    # pprint(new_edge_list)
    # print("=== lag ===")
    # pprint(lag)

    return new_edge_list, lag


##########
def assign_ip_lag(lag_list):
    """ Go through the lag list and convert it into a dict.  Assign interfaces and IP addresses"""

    lag_group_data = {}
    # print("=== lag_list ===")
    # pprint(lag_list)

    for lag_group in lag_list:

        # Get the next available PTP address
        ipv4_ptp_subnet = next(ipv4_address)
        ipv6_ptp_subnet = next(ipv6_address)
        ipv4_host = iter(ipv4_ptp_subnet.hosts())
        ipv6_host = iter(ipv6_ptp_subnet.hosts())

        # Assign individual addresses
        ipv4_1 = str(next(ipv4_host)) + "/30"
        ipv6_1 = str(next(ipv6_host)) + "/64"
        ipv4_2 = str(next(ipv4_host)) + "/30"
        ipv6_2 = str(next(ipv6_host)) + "/64"

        # print("=== lag_group ===")
        # pprint(lag_group)

        # Get device names
        device1 = lag_group[0][0]
        device2 = lag_group[0][2]

        # Get ae interface name from the iterator - keeps track of the next available ae interface.
        ae1 = ae_iterator(device1)
        ae2 = ae_iterator(device2)

        # Get the alias of the device so we can add a meaningful name to the description
        aliases1 = aliases[device1]
        aliases2 = aliases[device2]

        # Assign the description and addresses to the lag group
        lag_group_data.setdefault(device1, {})[ae1] = dict(
            description=aliases2, ipv4=ipv4_1, ipv6=ipv6_1)
        lag_group_data.setdefault(device2, {})[ae2] = dict(
            description=aliases1, ipv4=ipv4_2, ipv6=ipv6_2)

        # Assign the interfaces to the lag group
        for lag in lag_group:
            lag_group_data[lag[0]][ae1].setdefault(
                "interfaces", []).append(lag[1])
            lag_group_data[lag[2]][ae2].setdefault(
                "interfaces", []).append(lag[3])

    #pprint("=== lag_group_data ===")
    #pprint(lag_group_data)

    return (lag_group_data)

##########
def make_aliases():
    try:
        with open(args.resource_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                aliases[row["Name"]] = row["Alias"]
    except FileNotFoundError as e:
        print ("cannot find resource file",args.resource_file)
        print ("Please specify resource file location\n")
        parser.print_help()
        exit()


##########
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Assign IP addresses to JCL devices', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ipv4_p2p_subnet',
                        default="192.168.0.0/24", help='IPv4 address range')
    parser.add_argument(
        '--ipv6_p2p_subnet', default="2001:192:168:0::/56", help='IPv6 address range')
    parser.add_argument(
        '--ipv4_lo_subnet', default="10.255.255.0/24", help='IPv4 lo address range')
    parser.add_argument(
        '--ipv6_lo_subnet', default="2001:255:255:0::/64", help='IPv4 lo address range')
    parser.add_argument('--lag', action='store_true',
                        help='Bundle multiple edges into a LAG')
    parser.add_argument('--install', action='store_true',
                        help='Install to devices')
    parser.add_argument(
        '--resource_file', default="JCL-Sandbox-Resources.csv", help='JCL resource file')
    parser.add_argument('topo_file', nargs='?',
                        default="/etc/ansible/group_vars/all/topology.yaml", help='JCL topology file')
    args = parser.parse_args()

    ipv6_p2p_prefix_length = 64
    ipv4_p2p_prefix_length = 30

    # set up P2P and address iterables
    ipv4_address = iter(ipaddress.ip_network(
        args.ipv4_p2p_subnet).subnets(new_prefix=ipv4_p2p_prefix_length))
    ipv6_address = iter(ipaddress.ip_network(
        args.ipv6_p2p_subnet).subnets(new_prefix=ipv6_p2p_prefix_length))

    # set up lo0 address iterables
    ipv4_lo_address = iter(ipaddress.ip_network(
        args.ipv4_lo_subnet).subnets(new_prefix=32))
    ipv6_lo_address = iter(ipaddress.ip_network(
        args.ipv6_lo_subnet).subnets(new_prefix=128))
    # Skip the 0 address
    next(ipv4_lo_address)
    next(ipv6_lo_address)

    ae_iterator = ae_Iterator()

    aliases = {}

    make_aliases()

    # with open("topology.yaml", "r") as stream:
    try:
        with open(args.topo_file, "r") as stream:
            try:
                topo_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    except FileNotFoundError as e:
        print ("cannot find topo_file",args.topo_file)
        print ("Please specify topo_file location\n")
        parser.print_help()
        exit()

    edge_list = get_edge_list(topo_data)
    print("=== edge_list ===")
    pprint(edge_list)

    uniq_edge_list = remove_dup_edges(edge_list)
    print("=== uniq_edge_list ===")
    pprint(uniq_edge_list)

    jnpr_uniq_edge_list = remove_non_jnpr(uniq_edge_list)
    print("=== jnpr_uniq_edge_list ===")
    pprint(jnpr_uniq_edge_list)

    if args.lag:
        edge_list, lag_list = lag_interfaces(jnpr_uniq_edge_list)

        print("=== new_edge_list ===")
        pprint(edge_list)
        print("=== lag_list ===")
        pprint(lag_list)
    else:
        edge_list = jnpr_uniq_edge_list

    # router_interfaces = assign_ip(jnpr_uniq_edge_list)
    router_interfaces = assign_ip(edge_list)
    print("=== Router_interfaces ===")
    pprint(router_interfaces)

    for rtr in router_interfaces:
        print("===", rtr, "===")
        interface_config = generate_interface_configs( rtr, router_interfaces[rtr])
        print(interface_config)
        if (args.install):
            install_configs(rtr, interface_config)

    if args.lag:
        lag_interfaces = assign_ip_lag(lag_list)
        print("=== LAG interfaces ===")
        #pprint(lag_interfaces)
        for rtr in lag_interfaces:
            print("===", rtr, "===")
            interface_config = generate_lag_configs( rtr, lag_interfaces[rtr])
            print(interface_config)
            if (args.install):
                install_configs(rtr, interface_config)





