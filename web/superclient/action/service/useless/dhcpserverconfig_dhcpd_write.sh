#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interface)
            interface="$2"
            shift # past argument
            shift # past value
            ;;
        -ip|--ip_address)
            ip_address="$2"
            shift # past argument
            shift # past value
            ;;
        -mask|--subnet_mask)
            subnet_mask="$2"
            shift # past argument
            shift # past value
            ;;
        -from|--dhcp_ip_address_from)
            dhcp_ip_address_from="$2"
            shift # past argument
            shift # past value
            ;;
        -to|--dhcp_ip_address_to)
            dhcp_ip_address_to="$2"
            shift # past argument
            shift # past value
            ;;
        -cf|--dhcpd_config_file)
            dhcpd_config_file="$2"
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

exit_code=0

ifconfig $interface $ip_address netmask $subnet_mask up

ip_address_temp=$(echo -n $ip_address | sed 's/\([[:digit:]]\{1,3\}\(\.[[:digit:]]\{1,3\}\)\{2\}\.\)\([[:digit:]]\{1,3\}\)/\1/g')"0"

cat >> $dhcpd_config_file << EOF
authoritative;
subnet $ip_address_temp netmask $subnet_mask {
  range $dhcp_ip_address_from $dhcp_ip_address_to;
  option domain-name-servers $ip_address;
  option routers $ip_address;
  default-lease-time 3600;
  max-lease-time 86400;
}
EOF

exit $exit_code
