#!/bin/bash

this_file_path=$(eval "realpath $0")
this_dir_path=$(eval "dirname $this_file_path")

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -wc|--wpa_supplicant_config_file)
            wpa_supplicant_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        -wP|--wpa_supplicant_pid_file)
            wpa_supplicant_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        -wl|--wpa_supplicant_log_file)
            wpa_supplicant_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        -hc|--hostapd_config_file)
            hostapd_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        -hP|--hostapd_pid_file)
            hostapd_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        -hl|--hostapd_log_file)
            hostapd_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        -dP|--dnsmasq_pid_file)
            dnsmasq_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        -d8|--dnsmasq_log_file)
            dnsmasq_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        -dl|--dnsmasq_lease_file)
            dnsmasq_lease_file="$2"
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

# lanConfig
for dev in $($this_dir_path/interface_list.sh eth); do
    ifconfig $dev down
    ifconfig $dev:1 down
    ifconfig $dev:2 down
    ifconfig $dev:3 down
    ifconfig $dev:4 down
    sleep 1
done

# wlanConfig
nmcli radio wifi off
rfkill unblock wlan

if pgrep -f 'wpa_supplicant'; then
    killall 'wpa_supplicant' &>/dev/null
    sleep 1
fi

rm $wpa_supplicant_config_file
rm $wpa_supplicant_pid_file
rm $wpa_supplicant_log_file

for dev in $($this_dir_path/interface_list.sh wlan); do
    ifconfig $dev down
    ifconfig $dev:1 down
    ifconfig $dev:2 down
    ifconfig $dev:3 down
    ifconfig $dev:4 down
    sleep 1
done

# hotspotConfig
if pgrep -f 'hostapd'; then
    killall 'hostapd' &>/dev/null
    sleep 1
fi

rm $hostapd_config_file
rm $hostapd_pid_file
rm $hostapd_log_file

# dhcpServerConfig
if pgrep -f 'dnsmasq'; then
    killall 'dnsmasq' &>/dev/null
    sleep 1
fi

rm $dnsmasq_pid_file
rm $dnsmasq_log_file
rm $dnsmasq_lease_file

# dns
if [ -n "$(cat /etc/resolv.conf | grep '#MYDNS_')" ]; then
    sed -n -e '/#MYDNS_START/,/#MYDNS_END/!p' -i /etc/resolv.conf
    sleep 1
fi

# ip_forward 0
sysctl -w net.ipv4.ip_forward=0

# iptables reset
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

exit $exit_code
