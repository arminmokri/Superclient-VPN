#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --dhcp_module)
            dhcp_module="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_bridge)
            dnsmasq_bridge="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_interface)
            dnsmasq_interface="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_ip_address)
            dnsmasq_ip_address="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_subnet_mask)
            dnsmasq_subnet_mask="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_dhcp_ip_address_from)
            dnsmasq_dhcp_ip_address_from="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_dhcp_ip_address_to)
            dnsmasq_dhcp_ip_address_to="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_pid_file)
            dnsmasq_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_log_file)
            dnsmasq_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dnsmasq_lease_file)
            dnsmasq_lease_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_bridge)
            dhcpd_bridge="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_interface)
            dhcpd_interface="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_ip_address)
            dhcpd_ip_address="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_subnet_mask)
            dhcpd_subnet_mask="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_dhcp_ip_address_from)
            dhcpd_dhcp_ip_address_from="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_dhcp_ip_address_to)
            dhcpd_dhcp_ip_address_to="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_config_file)
            dhcpd_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_pid_file)
            dhcpd_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_log_file)
            dhcpd_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhcpd_lease_file)
            dhcpd_lease_file="$2"
            shift # past argument
            shift # past value
            ;;
        --named_config_file)
            named_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --named_log_file)
            named_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dns_server)
            dns_server="$2"
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


dnsmasq_res=1
if [ -n "$dnsmasq_interface" ]; then

    list_bridge=(`echo $dnsmasq_bridge | sed 's/,/\n/g'`)
    list_interface=(`echo $dnsmasq_interface | sed 's/,/\n/g'`)
    list_ip_address=(`echo $dnsmasq_ip_address | sed 's/,/\n/g'`)
    list_subnet_mask=(`echo $dnsmasq_subnet_mask | sed 's/,/\n/g'`)
    list_dhcp_ip_address_from=(`echo $dnsmasq_dhcp_ip_address_from | sed 's/,/\n/g'`)
    list_dhcp_ip_address_to=(`echo $dnsmasq_dhcp_ip_address_to | sed 's/,/\n/g'`)

    dhcp_range=""
    use_interface=""
    use_interface_list=""
    for i in "${!list_interface[@]}"; do
        temp_bridge=${list_bridge[$i]}
        temp_interface=${list_interface[$i]}
        temp_ip_address=${list_ip_address[$i]}
        temp_subnet_mask=${list_subnet_mask[$i]}
        temp_dhcp_ip_address_from=${list_dhcp_ip_address_from[$i]}
        temp_dhcp_ip_address_to=${list_dhcp_ip_address_to[$i]}

        if [ -n "$temp_bridge" ]; then
            brctl addbr $temp_bridge
            ifconfig $temp_bridge $temp_ip_address netmask $temp_subnet_mask up
            ifconfig $temp_interface up
            n=0
            until [ "$n" -ge 5 ]
            do
                brctl addif $temp_bridge $temp_interface
                sleep 5
                if [[ -n $(brctl show $temp_bridge | grep $temp_interface) ]]; then
                    break
                fi
                n=$((n+1))
            done
            use_interface=$temp_bridge
        else
            ifconfig $temp_interface $temp_ip_address netmask $temp_subnet_mask up
            use_interface=$temp_interface
        fi
        
        if [[ "$use_interface_list" == "" ]]; then
            use_interface_list=$use_interface
        else
            use_interface_list=$use_interface_list","$use_interface
        fi

        dhcp_range=$dhcp_range"--dhcp-range=interface:$use_interface,$temp_dhcp_ip_address_from,$temp_dhcp_ip_address_to,$temp_subnet_mask,24h "
        dhcp_option=$dhcp_option"--dhcp-option=$use_interface,3,$temp_ip_address --dhcp-option=$use_interface,6,$temp_ip_address "
    done  

    if [[ $log == "yes" ]]; then
        # --no-negcache --strict-order --clear-on-reload --log-queries
        dnsmasq --port=0 \
        --dhcp-authoritative --log-dhcp --bind-interfaces --except-interface=lo \
        --interface=$use_interface_list --listen-address=$dnsmasq_ip_address $dhcp_range $dhcp_option \
        --log-facility=$dnsmasq_log_file --pid-file=$dnsmasq_pid_file --dhcp-leasefile=$dnsmasq_lease_file
        dnsmasq_res=$?
    else
        # --no-negcache --strict-order --clear-on-reload --log-queries
        dnsmasq --port=0 \
        --dhcp-authoritative --log-dhcp --bind-interfaces --except-interface=lo \
        --interface=$use_interface_list --listen-address=$dnsmasq_ip_address $dhcp_range $dhcp_option \
        --pid-file=$dnsmasq_pid_file --dhcp-leasefile=$dnsmasq_lease_file &> /dev/null
        dnsmasq_res=$?
    fi
else
    dnsmasq_res=0
fi

dhcpd_res=1
if [ -n "$dhcpd_interface" ]; then

    list_bridge=(`echo $dhcpd_bridge | sed 's/,/\n/g'`)
    list_interface=(`echo $dhcpd_interface | sed 's/,/\n/g'`)
    list_ip_address=(`echo $dhcpd_ip_address | sed 's/,/\n/g'`)
    list_subnet_mask=(`echo $dhcpd_subnet_mask | sed 's/,/\n/g'`)
    list_dhcp_ip_address_from=(`echo $dhcpd_dhcp_ip_address_from | sed 's/,/\n/g'`)
    list_dhcp_ip_address_to=(`echo $dhcpd_dhcp_ip_address_to | sed 's/,/\n/g'`)

    cat > $dhcpd_config_file << EOF
authoritative;
EOF

    use_interface=""
    use_interface_list=""
    for i in "${!list_interface[@]}"; do
        temp_bridge=${list_bridge[$i]}
        temp_interface=${list_interface[$i]}
        temp_ip_address=${list_ip_address[$i]}
        temp_subnet_mask=${list_subnet_mask[$i]}
        temp_dhcp_ip_address_from=${list_dhcp_ip_address_from[$i]}
        temp_dhcp_ip_address_to=${list_dhcp_ip_address_to[$i]}

        if [ -n "$temp_bridge" ]; then
            brctl addbr $temp_bridge
            ifconfig $temp_bridge $temp_ip_address netmask $temp_subnet_mask up
            ifconfig $temp_interface up
            n=0
            until [ "$n" -ge 5 ]
            do
                brctl addif $temp_bridge $temp_interface
                sleep 5
                if [[ -n $(brctl show $temp_bridge | grep $temp_interface) ]]; then
                    break
                fi
                n=$((n+1))
            done
            use_interface=$temp_bridge
        else
            ifconfig $temp_interface $temp_ip_address netmask $temp_subnet_mask up
            use_interface=$temp_interface
        fi
        
        if [[ "$use_interface_list" == "" ]]; then
            use_interface_list=$use_interface
        else
            use_interface_list=$use_interface_list" "$use_interface
        fi

        network_range=$(echo -n $temp_ip_address | sed 's/\([[:digit:]]\{1,3\}\(\.[[:digit:]]\{1,3\}\)\{2\}\.\)\([[:digit:]]\{1,3\}\)/\1/g')"0"
    
        cat >> $dhcpd_config_file << EOF
subnet $network_range netmask $temp_subnet_mask {
  range $temp_dhcp_ip_address_from $temp_dhcp_ip_address_to;
  option routers $temp_ip_address;
  option domain-name-servers $temp_ip_address;
  default-lease-time 86400;
  max-lease-time 86400;
}
EOF
    done

    touch $dhcpd_lease_file
    
    if [[ $log == "yes" ]]; then
        dhcpd -cf $dhcpd_config_file -pf $dhcpd_pid_file -tf $dhcpd_log_file -lf $dhcpd_lease_file $use_interface_list
        dhcpd_res=$?
    else
        dhcpd -cf $dhcpd_config_file -pf $dhcpd_pid_file -lf $dhcpd_lease_file $use_interface_list &> /dev/null
        dhcpd_res=$?
    fi

else
    dhcpd_res=0
fi

named_res=1
if [[ $dns_server != "" ]]; then

    str_listen=""

    list_ip_address=(`echo $dnsmasq_ip_address | sed 's/,/\n/g'`)
    for i in "${!list_ip_address[@]}"; do
        str_listen=$str_listen"        ${list_ip_address[$i]};"$'\n'
    done

    list_ip_address=(`echo $dhcpd_ip_address | sed 's/,/\n/g'`)
    for i in "${!list_ip_address[@]}"; do
        str_listen=$str_listen"        ${list_ip_address[$i]};"$'\n'
    done

    str_dns=""
    for item in ${dns_server//,/ } ; do
        str_dns=$str_dns"        $item;"$'\n'
    done

    cat > $named_config_file << EOF
options {
    directory "/var/cache/bind";

    recursion yes;

    listen-on {
$str_listen
    };

    allow-transfer { none; };

    forwarders {
$str_dns
    };

    forward only;
    
    resolver-query-timeout 20;

    dnssec-enable no;
    dnssec-validation no;
    dnssec-lookaside auto;
};

zone "." {
        type hint;
        file "/usr/share/dns/root.hints";
};

// be authoritative for the localhost forward and reverse zones, and for
// broadcast zones as per RFC 1912

zone "localhost" {
        type master;
        file "/etc/bind/db.local";
};

zone "127.in-addr.arpa" {
        type master;
        file "/etc/bind/db.127";
};

zone "0.in-addr.arpa" {
        type master;
        file "/etc/bind/db.0";
};

zone "255.in-addr.arpa" {
        type master;
        file "/etc/bind/db.255";
};
EOF

    if [[ $log == "yes" ]]; then
        named -c $named_config_file -u bind -L $named_log_file
        named_res=$?
    else
        named -c $named_config_file -u bind &> /dev/null
        named_res=$?
    fi
    
else
    named_res=0
fi

if [[ $dnsmasq_res == 0 ]] && [[ $dhcpd_res == 0 ]] && [[ $named_res == 0 ]]; then
    exit_code=0
else
    exit_code=1
fi

exit $exit_code
