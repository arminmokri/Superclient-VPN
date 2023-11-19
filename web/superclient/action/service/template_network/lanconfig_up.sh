#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --interface)
            interface="$2"
            shift # past argument
            shift # past value
            ;;
        --dhclient_config_file)
            dhclient_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhclient_pid_file)
            dhclient_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhclient_lease_file)
            dhclient_lease_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhclient_log_file)
            dhclient_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcp)
            dhcp="yes"
            shift # past argument
            ;;
        --default_gateway_mode)
            default_gateway_mode="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcp_set_default_gateway)
            dhcp_set_default_gateway="yes"
            shift # past argument
            ;;
        --ip_address_1)
            ip_address_1="$2"
            shift # past argument
            shift # past value
            ;;
        --subnet_mask_1)
            subnet_mask_1="$2"
            shift # past argument
            shift # past value
            ;;
        --ip_address_2)
            ip_address_2="$2"
            shift # past argument
            shift # past value
            ;;
        --subnet_mask_2)
            subnet_mask_2="$2"
            shift # past argument
            shift # past value
            ;;
        --ip_address_3)
            ip_address_3="$2"
            shift # past argument
            shift # past value
            ;;
        --subnet_mask_3)
            subnet_mask_1="$2"
            shift # past argument
            shift # past value
            ;;
        --ip_address_4)
            ip_address_4="$2"
            shift # past argument
            shift # past value
            ;;
        --subnet_mask_4)
            subnet_mask_1="$2"
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

exit_code=0

# dhcp
dhcp_res=0
if [[ $dhcp == "yes" ]]; then
    ifconfig $interface up
    cat > $dhclient_config_file << EOF
retry 10;

option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;

send host-name = gethostname();
request subnet-mask, broadcast-address, time-offset, routers,
	domain-name, domain-name-servers, domain-search, host-name,
	dhcp6.domain-search, dhcp6.fqdn, dhcp6.sntp-servers,
	netbios-name-servers, netbios-scope, interface-mtu,
	rfc3442-classless-static-routes, ntp-servers;
EOF

    if [[ $default_gateway_mode == "manual" ]] || [[ $dhcp_set_default_gateway == "" ]]; then
        cat >> $dhclient_config_file << EOF

supersede routers 1,1,1,1;
supersede domain-name-servers 8.8.8.8;
EOF
    elif [[ $default_gateway_mode == "dhcp" ]] && [[ $dhcp_set_default_gateway == "yes" ]]; then
        cat >> $dhclient_config_file << EOF

require routers, domain-name-servers;
EOF
        ip route add 169.254.0.0/16 dev $interface metric 1000
    fi

    if [[ $log == "yes" ]]; then
        dhclient -cf $dhclient_config_file -pf $dhclient_pid_file -lf $dhclient_lease_file -v $interface 2> $dhclient_log_file &
    else
        dhclient -cf $dhclient_config_file -pf $dhclient_pid_file -lf $dhclient_lease_file $interface 2> /dev/null &
    fi
fi

# static 1
ip1_res=0
if [[ -n $ip_address_1 ]] && [[ -n $subnet_mask_1 ]]; then
    ifconfig $interface:1 $ip_address_1 netmask $subnet_mask_1 up
    ip1_res=$?
fi

# static 2
ip2_res=0
if [[ -n $ip_address_2 ]] && [[ -n $subnet_mask_2 ]]; then
    ifconfig $interface:2 $ip_address_2 netmask $subnet_mask_2 up
    ip2_res=$?
fi

# static 3
ip3_res=0
if [[ -n $ip_address_3 ]] && [[ -n $subnet_mask_3 ]]; then
    ifconfig $interface:3 $ip_address_3 netmask $subnet_mask_3 up
    ip3_res=$?
fi

# static 4
ip4_res=0
if [[ -n $ip_address_4 ]] && [[ -n $subnet_mask_4 ]]; then
    ifconfig $interface:4 $ip_address_4 netmask $subnet_mask_4 up
    ip4_res=$?
fi

if [[ $dhcp_res == 0 ]] && [[ $ip1_res == 0 ]] && [[ $ip2_res == 0 ]] && [[ $ip3_res == 0 ]] && [[ $ip4_res == 0 ]]; then
    exit_code=0
else
    exit_code=1
fi

exit $exit_code
