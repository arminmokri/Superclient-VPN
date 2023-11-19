#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1") # save positional arg
            shift # past argument
            ;;
    esac
done
set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

sysctl -w net.ipv4.ip_forward=0

iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

if pgrep -f 'redsocks'; then
    killall 'redsocks' &>/dev/null
    sleep 1
fi

if pgrep -f 'DNS2SOCKS'; then
    killall 'DNS2SOCKS' &>/dev/null
    sleep 1
fi

if [ -n "$(ip rule show table 100)" ]; then
    ip rule  del   table 100 &>/dev/null
    ip route flush table 100 &>/dev/null
    sleep 1
fi

if pgrep -f 'badvpn-tun2socks'; then
    killall 'badvpn-tun2socks' &>/dev/null
    sleep 1
fi

if [ -n "$(ip link show | grep tun0)" ]; then
    ifconfig tun0 down &>/dev/null
    ip link set tun0 down &>/dev/null
    ip link delete tun0 &>/dev/null
    sleep 1
fi

list=$(sysctl -a | grep "\.rp_filter")
for item in $list
do
	if [[ "$item" == *"rp_filter"* ]]; then
		sysctl -w $item=0
	fi
done

exit 0
