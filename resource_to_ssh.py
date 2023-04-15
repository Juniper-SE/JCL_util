#!/usr/bin/python3

import argparse
import csv
import re


parser = argparse.ArgumentParser(description='create SSH config file from JCL resource file. (email from JCL)',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('resource_file', nargs='?', default="JCL-Sandbox-Resources.csv", help='JCL resource file')
args = parser.parse_args()


rematch_name = r'^(HelperVM)|(Ubuntu)|(vMX)'


with open(args.resource_file) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if not(row["Service"] == "SSH"):
            continue
        if not(re.search(rematch_name, row["Name"])):
            #print ("Skip ",row["Alias"])
            continue

        print("Host",row['Alias'], row['Name'])
        print("\t", "Hostname ", row['PubAddr'])
        print("\t", "Port ", row['PubPort'])
        print("\t", "User ", row['Username'])
        print("\t", "# Passwd ", row['Password'])
        print("\t", "ForwardAgent yes")
        print("\t", "ForwardX11 yes")
        print("\t", "TCPKeepAlive yes")
        print("\t", "ServerAliveInterval 60")
        print("\t", "StrictHostKeyChecking no")
        print("\t", "UserKnownHostsFile /dev/null")
        print("")

