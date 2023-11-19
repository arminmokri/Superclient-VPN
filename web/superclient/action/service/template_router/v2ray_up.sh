#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --pid_file)
            pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --log_file)
            log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --timeout)
            timeout="$2"
            shift # past argument
            shift # past value
            ;;
        --try_count)
            try_count="$2"
            shift # past argument
            shift # past value
            ;;
        --config)
            config="$2"
            shift # past argument
            shift # past value
            ;;
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
        --v2ray_outbounds_address)
            v2ray_outbounds_address="$2"
            shift # past argument
            shift # past value
            ;;
        --tun2socks)
            tun2socks="$2"
            shift # past argument
            shift # past value
            ;;
        --tun2socks_log_file)
            tun2socks_log_file="$2"
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
        --log)
            log="yes"
            shift # past argument
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

exit_code=1

if [[ $log == "yes" ]]; then
    v2ray run -config $config &> $log_file &
    pid=$!
    exit_code=$?
else
    v2ray run -config $config &> /dev/null &
    pid=$!
    exit_code=$?
fi

if [ "$exit_code" == 0 ]; then

    ########################################################################
    # v2ray pid
    ########################################################################
    echo -n $pid > $pid_file

    ########################################################################
    # Define various configuration parameters.
    ########################################################################

    default_gateway=$(route -n | grep 'UG' | awk {'print $2'} | head -n 1 | tr -d '\n')
    v2ray_inbounds_ip="127.0.0.1"
    v2ray_outbounds_ip=""
    v2ray_outbounds_host=""
    reg="[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    if [[ $v2ray_outbounds_address =~ $reg ]]; then
        v2ray_outbounds_ip=$v2ray_outbounds_address
    else
        v2ray_outbounds_host=$v2ray_outbounds_address
        v2ray_outbounds_ip=$(dig +short $v2ray_outbounds_host)
        echo $v2ray_outbounds_ip" "$v2ray_outbounds_host >> /etc/hosts
    fi

    ########################################################################
    # start dns
    ########################################################################

    if [[ -n "$dns_server" ]] && [[ -n "$dns_log" ]]; then

        # DNS2SOCKS
        if [[ $log == "yes" ]]; then
            DNS2SOCKS $v2ray_inbounds_ip:$v2ray_inbounds_port $dns_server 127.0.0.1:5300 /l:$dns_log &> /dev/null &
        else
            DNS2SOCKS $v2ray_inbounds_ip:$v2ray_inbounds_port $dns_server 127.0.0.1:5300 &> /dev/null &
        fi

        # iptables
        iptables -t nat -A OUTPUT -p tcp --dport 53 -j REDIRECT --to-port 5300
        iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-port 5300
    fi

    ########################################################################
    # start tuntap
    ########################################################################

    ip tuntap add dev $vpn_interface mode tun
    ip addr add dev $vpn_interface 10.0.0.1/24
    ip link set dev $vpn_interface up

    route add -net 0.0.0.0 netmask 0.0.0.0 dev $vpn_interface
    ip route add $v2ray_outbounds_ip via $default_gateway

    sleep 1

    ########################################################################
    # start tun2socks
    ########################################################################
    
    if [[ $tun2socks == "badvpn-tun2socks" ]]; then
        if [[ $log == "yes" ]]; then
            badvpn-tun2socks --tundev $vpn_interface --netif-ipaddr 10.0.0.2 --netif-netmask 255.255.255.0 --socks-server-addr \
            $v2ray_inbounds_ip:$v2ray_inbounds_port --loglevel 4 --socks5-udp &> $tun2socks_log_file &
        else
            badvpn-tun2socks --tundev $vpn_interface --netif-ipaddr 10.0.0.2 --netif-netmask 255.255.255.0 --socks-server-addr \
            $v2ray_inbounds_ip:$v2ray_inbounds_port --loglevel 0 --socks5-udp &> /dev/null &
        fi
    elif [[ $tun2socks == "go-tun2socks" ]]; then
        if [[ $log == "yes" ]]; then
            go-tun2socks -loglevel info -tunName $vpn_interface -proxyServer $v2ray_inbounds_ip:$v2ray_inbounds_port -proxyType socks \
            -tunAddr 10.0.0.2 -tunGw 10.0.0.1 -tunMask 255.255.255.0 -tunPersist -udpTimeout 10000ms &> $tun2socks_log_file &
        else
            go-tun2socks -loglevel none -tunName $vpn_interface -proxyServer $v2ray_inbounds_ip:$v2ray_inbounds_port -proxyType socks \
            -tunAddr 10.0.0.2 -tunGw 10.0.0.1 -tunMask 255.255.255.0 -tunPersist -udpTimeout 10000ms &> /dev/null &
        fi
    elif [[ $tun2socks == "tun2socks" ]]; then
        if [[ $log == "yes" ]]; then
            tun2socks -loglevel info -device tun://$vpn_interface -proxy socks5://$v2ray_inbounds_ip:$v2ray_inbounds_port -udp-timeout 10s -tcp-rcvbuf 5840iB -tcp-sndbuf 8192iB &> $tun2socks_log_file &
        else
            tun2socks -loglevel silent -device tun://$vpn_interface -proxy socks5://$v2ray_inbounds_ip:$v2ray_inbounds_port -udp-timeout 10s -tcp-rcvbuf 5840iB -tcp-sndbuf 8192iB &> /dev/null &
        fi
    fi

    ########################################################################
    # start iptables
    ########################################################################
    
    # .rp_filter 2
    list=$(sysctl -a | grep "\.rp_filter")
    for item in $list
    do
        if [[ "$item" == *"rp_filter"* ]]; then
            sysctl -w $item=0
        fi
    done

fi

exit $exit_code
