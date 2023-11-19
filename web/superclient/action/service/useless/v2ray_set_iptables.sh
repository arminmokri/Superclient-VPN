#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --vpn_interface)
            vpn_interface="$2"
            shift # past argument
            shift # past value
            ;;
        --v2ray_inbounds_port)
            v2ray_inbounds_port="$2"
            shift # past argument
            shift # past value
            ;;
        --v2ray_outbounds_ip)
            v2ray_outbounds_ip="$2"
            shift # past argument
            shift # past value
            ;;
        --badvpn_tun2socks_log_file)
            badvpn_tun2socks_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dns_mode)
            dns_mode="$2"
            shift # past argument
            shift # past value
            ;;
        --dns_server)
            dns_server="$2"
            shift # past argument
            shift # past value
            ;;
        --dns_log)
            dns_log="$2"
            shift # past argument
            shift # past value
            ;;
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

########################################################################
# Define various configuration parameters.
########################################################################

default_gateway=$(route -n | grep 'UG' | awk {'print $2'} | head -n 1 | tr -d '\n')
v2ray_inbounds_ip="127.0.0.1"

########################################################################
# start dns
########################################################################

if [ -n "$dns_server" ] && [ -n "$dns_log" ]; then
	if pgrep -f 'DNS2SOCKS'; then
		killall 'DNS2SOCKS' &>/dev/null
		sleep 1
	fi

	#
	DNS2SOCKS $v2ray_inbounds_ip:$v2ray_inbounds_port $dns_server 127.0.0.1:5300 /l:$dns_log &>/dev/null &

	# iptables
	iptables -t nat -A OUTPUT -p tcp --dport 53 -j REDIRECT --to-port 5300
	iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-port 5300
fi

########################################################################
# start tuntap
########################################################################

if [ -n "$(ip link show | grep $vpn_interface)" ]; then
    ifconfig tun0 down &>/dev/null
    ip link set tun0 down &>/dev/null
    ip link delete tun0 &>/dev/null
	sleep 1
fi

ip tuntap add dev $vpn_interface mode tun
ip addr add dev $vpn_interface 10.0.0.1/24
ip link set dev $vpn_interface up

route add -net 0.0.0.0 netmask 0.0.0.0 dev $vpn_interface
ip route add $v2ray_outbounds_ip via $default_gateway

sleep 1

########################################################################
# start badvpn-tun2socks
########################################################################

if pgrep -f 'badvpn-tun2socks'; then
    killall 'badvpn-tun2socks' &>/dev/null
	sleep 1
fi

badvpn-tun2socks --tundev $vpn_interface --netif-ipaddr 10.0.0.2 --netif-netmask 255.255.255.0 --socks-server-addr $v2ray_inbounds_ip:$v2ray_inbounds_port --loglevel 3 --socks5-udp &>$badvpn_tun2socks_log_file &>/dev/null &

########################################################################
# start iptables
########################################################################

# policy
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# ip_forward 1
sysctl -w net.ipv4.ip_forward=1

# .rp_filter 2
list=$(sysctl -a | grep "\.rp_filter")
for item in $list
do
	if [[ "$item" == *"rp_filter"* ]]; then
		sysctl -w $item=2
	fi
done

exit 0
