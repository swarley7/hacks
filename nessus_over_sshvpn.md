# Remote nessus

Situation: you have to perform a Nessus scan on a remote network. Proxychains doesn't work so good (at least recent versions of nessus suck with it). Also other testing tools suck at dealing with SOCKS proxies etc.

How do?

# VPN over SSH

OpenSSH Server (recent versions) supports the creation of Tun adaptors, effectively turning the ssh tunnel into a proper vpn tunnel.

This guide:
  - Assumes you have two hosts (a kali vm, and the VPN endpoint jumpbox)
  - Assumes you have root access to both hosts
  - Assumes you're permitted to make changes to the host (authorisation is important!)
  
*Note:* the changes detailed in this guide are not persistent (nor are they intended to be). If you require persistent VPN access, use a proper solution (e.g. openvpn or wireguard). This is for pentesters in a pinch. 
A reboot should be sufficient to clean the config up.

Requires a bit of setup on the server and client end (assumed you have root on the jumpbox).

# VPN Endpoint: enable PermitTunnel in the SSHD Config
`sudo sh -c 'echo "PermitTunnel yes" >>/etc/ssh/sshd_config'`

# VPN Endpoint: Configure tun adaptor and enable IP forwarding

*Note:* if 10.1.1.0/30 conflicts with the networks you're on or accessing, choose another /30 for here and ensure to update both instances accordingly.
`sudo ip tuntap add dev tun0 mode tun`
`sudo ifconfig tun0 10.1.1.1 pointopoint 10.1.1.2 netmask 255.255.255.252`
`sudo sysctl -w net.ipv4.ip_forward=1`

# Setup NAT on VPN endpoint (this will ensure the client can route to networks accessible by the VPN host)
*Note:* 
  - eth0 == VPN endpoint's WAN/LAN adaptor attached to the destination remote networks
  - tun0 == VPN endpoint's Tun adaptor that the Kali VM will connect to

```
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i tun0 -o eth0 -j ACCEPT
```

# Kali VM: Connect the SSH VPN
`ssh -f -w 0:0 remote-host.example.com true`

# Kali VM: Configure tun adaptor and IP address
`sudo ip tuntap add dev tun0 mode tun`
`sudo ifconfig tun0 10.1.1.2 pointopoint 10.1.1.1 netmask 255.255.255.252`


# Enable routing on Kali vm:

*Note:* I've used the subnet 172.16.0.0/12 as an example; this should be your remote network(s) that you are trying to access via the VPN
```
sudo route add -net 172.16.0.0/12 gw 10.1.1.1
sudo sysctl -w net.ipv4.ip_forward=1
```


# Extra points - I don't like doing stuff from VMs
Now, if you're like me and prefer to use a mac For everything; you can enable IP forwarding and NAT on the Kali VM to allow your mac to communicate directly with the remote networks:


## Kali VM: setup NAT
```
iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE
iptables -A FORWARD -i tun0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0 -o tun0 -j ACCEPT
```

## Kali VM: setup ip forwarding

`sudo sysctl -w net.ipv4.ip_forward=1`


## macOS - set up routes (assume Kali VM has an IP address accessible to macOS on 192.168.1.1)
`sudo route add 172.16.0.0/12 192.168.1.1`

Now you should be able to ping/nmap/nessus the destination networks from your Kali VM or your mac!
