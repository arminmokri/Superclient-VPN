#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
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

# dhcpServerConfig
if [ -n "$(pgrep -f 'dnsmasq')" ]; then
    killall 'dnsmasq' &>/dev/null
    sleep 1
fi

if [ -f "$dnsmasq_pid_file" ]; then
    rm $dnsmasq_pid_file
fi
if [ -f "$dnsmasq_log_file" ]; then
    rm $dnsmasq_log_file
fi
if [ -f "$dnsmasq_lease_file" ]; then
    rm $dnsmasq_lease_file
fi

if [ -n "$(pgrep -f 'dhcpd')" ]; then
    killall 'dhcpd' &>/dev/null
    sleep 1
fi

if [ -f "$dhcpd_config_file" ]; then
    rm $dhcpd_config_file
fi
if [ -f "$dhcpd_pid_file" ]; then
    rm $dhcpd_pid_file
fi
if [ -f "$dhcpd_log_file" ]; then
    rm $dhcpd_log_file
fi
if [ -f "$dhcpd_lease_file" ]; then
    rm $dhcpd_lease_file
fi

if [ -n "$(pgrep -f 'named')" ]; then
    killall 'named' &>/dev/null
    sleep 1
fi

if [ -f "$named_config_file" ]; then
    rm $named_config_file
fi
if [ -f "$named_log_file" ]; then
    rm $named_log_file
fi

if [[ $(brctl show | tail -n +2 | awk '{print $1}' | wc -l | tr -d '\n') != "0" ]]; then
    for br_name in $(brctl show | tail -n +2 | awk '{print $1}')
    do
        ifconfig $br_name down
        brctl delbr $br_name
    done
fi

exit $exit_code
