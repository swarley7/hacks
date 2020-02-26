import netaddr
import subprocess
import sys
import argparse

# usage sudo python3 addroutes.py <file containing ipaddresses / networks> <gateway_ip address>

parser = argparse.ArgumentParser(description='Adds routes to remote nets')

parser.add_argument("-d", action="store_true", help="deletes routes")
parser.add_argument("input", help="input list of ip addresses / subnets")
parser.add_argument("gw", help="Gateway address to use for routes")

args = parser.parse_args()

input_list = open(args.input).readlines()
nets = {}
for i in input_list:
    x = ".".join(i.split(".")[:2])
    if x in nets:
        nets[x].append(i.strip())
    else:
        nets[x] = [i.strip()]

ranges = []
for k,v in nets.items():
    if len(v) == 1:
        x = ".".join(i.split(".")[:3])
        x = f"{x}.0/24"
        # print(x)
        ranges.append(x)
        continue
    spanning_cidr = netaddr.spanning_cidr(v)
    ranges.append(spanning_cidr)
    # print(spanning_cidr)

cmd = "add"
if args.d:
    cmd = "delete"
for i in ranges:
    subprocess.call(["route", cmd, str(i), args.gw])