#!/bin/bash

this_file_path=$(eval "realpath $0")
this_dir_path=$(eval "dirname $this_file_path")

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --wpa_supplicant_config_file)
            wpa_supplicant_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --wpa_supplicant_pid_file)
            wpa_supplicant_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --dhclient_lease_file)
            dhclient_lease_file="$2"
            shift # past argument
            shift # past value
            ;;
        --wpa_supplicant_log_file)
            wpa_supplicant_log_file="$2"
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
        --dhclient_log_file)
            dhclient_log_file="$2"
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

# wlanConfig
nmcli radio wifi off
rfkill unblock wlan

if [ -n "$(pgrep -f 'dhclient')" ]; then
    killall 'dhclient' &>/dev/null
    sleep 1
fi

if [ -f $dhclient_config_file ]; then
    rm $dhclient_config_file
fi
if [ -f $dhclient_pid_file ]; then
    rm $dhclient_pid_file
fi
if [ -f $dhclient_lease_file ]; then
    rm $dhclient_lease_file
fi
if [ -f $dhclient_log_file ]; then
    rm $dhclient_log_file
fi

if [ -n "$(pgrep -f 'wpa_supplicant')" ]; then
    killall 'wpa_supplicant' &>/dev/null
    sleep 1
fi

if [ -f $wpa_supplicant_config_file ]; then
    rm $wpa_supplicant_config_file
fi
if [ -f $wpa_supplicant_pid_file ]; then
    rm $wpa_supplicant_pid_file
fi
if [ -f $wpa_supplicant_log_file ]; then
    rm $wpa_supplicant_log_file
fi

for dev in $($this_dir_path/interface_list.sh wlan | awk '{ print length(), $0 | "sort -n" }' | awk '{ print $2 }'); do
    ifconfig $dev:1 0.0.0.0 up
    ifconfig $dev:2 0.0.0.0 up
    ifconfig $dev:3 0.0.0.0 up
    ifconfig $dev:4 0.0.0.0 up
    ifconfig $dev 0.0.0.0 up
    sleep 1
done

exit $exit_code
