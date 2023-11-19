#!/bin/bash

########################################################################
# This bash script will create a socksifying router and pass all subnet
# traffic over an ssh tunnel to a server at a different location through
# a socks5 proxy. As the script is now written, local traffic is not
# proxied, however, make the change noted below and it will be.
#
# Assumptions here are that you are using a laptop with an internet
# connection on eth0, and an additional wired ethernet port wlan0.
#
# The script requires that a dhcp server be running using the
# isc-dhcp-server package on ubuntu, or equivalent on other O/S varieties.
# This dhcp server will serve addresses on wlan0 to nodes trying to
# connect.  Either that or all of the subnet clients have to have static
# addresses. To configure dhcpd, add the following to /etc/dhcp/dhcpd.conf
# (changing the subnet address as appropriate):
#
#subnet 192.168.1.0 netmask 255.255.255.0 {
#  range 192.168.1.10 192.168.1.100;
#  range 192.168.1.150 192.168.1.200;
#  option routers 192.168.1.254;
#  option broadcast-address 192.168.1.255;
#}
#
# Also, the script requires the redsocks, openssh-client, and iptables
# packages be installed as well.
#
# Finally, you need to edit /etc/sysctl.conf as follows:
#
# Uncomment the next line to enable packet forwarding for IPv4
# net.ipv4.ip_forward=1
########################################################################

########################################################################
# Define various configuration parameters.
########################################################################

SOCKS_PORT=${1}
SUBNET_INTERFACE=${2}
SUBNET_PORT_ADDRESS=${3}
SUBNET_PORT_NETMASK=${4}
INTERNET_INTERFACE=${5}
DNSServer="8.8.8.8"

########################################################################
#standard router setup - sets up subnet SUBNET_PORT_ADDRESS/24 on wlan0
########################################################################

# note - if you just want a standard router without the proxy/tunnel
# business, you only need to execute this block of code.

sysctl -w net.ipv4.ip_forward=1

iptables -A FORWARD -o $INTERNET_INTERFACE -i $SUBNET_INTERFACE -s $SUBNET_PORT_ADDRESS/$SUBNET_PORT_NETMASK -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A POSTROUTING -t nat -j MASQUERADE

########################################################################
#redsocks configuration
########################################################################

REDSOCKS_TCP_PORT=$(expr $SOCKS_PORT + 1)
TMP=/tmp/subnetproxy ; mkdir -p $TMP
REDSOCKS_LOG=$TMP/redsocks.log
REDSOCKS_CONF=$TMP/redsocks.conf

cat >$REDSOCKS_CONF <<EOF
base {
  log_info = on;
  log = "file:$REDSOCKS_LOG";
  daemon = on;
  redirector = iptables;
}
redsocks {
  local_ip = 0.0.0.0;
  local_port = $REDSOCKS_TCP_PORT;
  ip = 127.0.0.1;
  port = $SOCKS_PORT;
  type = socks5;
}
EOF

# To use tor just change the redsocks output port from 1080 to 9050 and
# replace the ssh tunnel with a tor instance.

########################################################################
# start redsocks
########################################################################

if pgrep redsocks; then
    killall redsocks
    sleep 1
fi

redsocks -c $REDSOCKS_CONF &>/dev/null &

########################################################################
# proxy iptables setup
########################################################################

# create the REDSOCKS target
iptables -t nat -N REDSOCKS

# don't route unroutable addresses
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

# redirect statement sends everything else to the redsocks
# proxy input port
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports $REDSOCKS_TCP_PORT
iptables -t nat -A REDSOCKS -p udp -j REDIRECT --to-ports $REDSOCKS_TCP_PORT

# if it came in on wlan0, and it is tcp, send it to REDSOCKS
iptables -t nat -A PREROUTING -i $SUBNET_INTERFACE -p tcp -j REDSOCKS
iptables -t nat -A PREROUTING -i $SUBNET_INTERFACE -p udp -j REDSOCKS

# Use this one instead of the above if you want to proxy the local
# networking in addition to the subnet stuff. Redsocks listens on
# all interfaces with local_ip = 0.0.0.0 so no other changes are
# necessary.
#iptables -t nat -A PREROUTING -p tcp -j REDSOCKS

# don't forget to accept the tcp packets from wlan0
iptables -A INPUT -i $SUBNET_INTERFACE -p tcp --dport $REDSOCKS_TCP_PORT -j ACCEPT
iptables -A INPUT -i $SUBNET_INTERFACE -p udp --dport $REDSOCKS_TCP_PORT -j ACCEPT


# dns2socks
if pgrep DNS2SOCKS; then
    killall DNS2SOCKS
    sleep 1
fi

DNS2SOCKS 127.0.0.1:$SOCKS_PORT $DNSServer 127.0.0.1:5300 &>/dev/null &

# dns2socks iptables
iptables -t nat -A OUTPUT -p tcp --dport 53 -j REDIRECT --to-port 5300
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-port 5300

exit 0
