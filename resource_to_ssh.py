#!/usr/bin/python3

import csv
import re


rematch_name = r'^(HelperVM)|(Ubuntu)|(vMX)'


with open('JCL-Sandbox-Resources.csv') as csvfile:
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
        print("\t", "#ServerAliveInterval 300")

