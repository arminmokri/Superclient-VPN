#!/bin/bash

timedatectl set-ntp 0
date -s "1970-02-05 16:55:03"

sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A  POSTROUTING -o tun0 -j MASQUERADE
openconnect --protocol=anyconnect --background cisco4.dr-infoo.com:510 --user=greenmile
