#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --interface)
            interface="$2"
            shift # past argument
            shift # past value
            ;;
        --ssid)
            ssid="$2"
            shift # past argument
            shift # past value
            ;;
        --wpa_passphrase)
            wpa_passphrase="$2"
            shift # past argument
            shift # past value
            ;;
        --channel)
            channel="$2"
            shift # past argument
            shift # past value
            ;;
        --country_code)
            country_code="$2"
            shift # past argument
            shift # past value
            ;;
        --hostapd_config_file)
            hostapd_config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --hostapd_pid_file)
            hostapd_pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --hostapd_log_file)
            hostapd_log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --mac_address_filter_mode)
            mac_address_filter_mode="$2"
            shift # past argument
            shift # past value
            ;;
        --mac_address_filter_list)
            mac_address_filter_list="$2"
            shift # past argument
            shift # past value
            ;;
        --hostapd_accept_file)
            hostapd_accept_file="$2"
            shift # past argument
            shift # past value
            ;;
        --hostapd_deny_file)
            hostapd_deny_file="$2"
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

if [[ $mac_address_filter_mode == "disable" ]]; then
    macaddr_acl=0
    touch $hostapd_accept_file
    touch $hostapd_deny_file
elif [[ $mac_address_filter_mode == "block" ]]; then
    macaddr_acl=0
    touch $hostapd_accept_file
    str=""
    for item in ${mac_address_filter_list//,/ } ; do
        str=$str"$item\n"
    done
    echo -e $str > $hostapd_deny_file
elif [[ $mac_address_filter_mode == "accept" ]]; then
    macaddr_acl=1
    str=""
    for item in ${mac_address_filter_list//,/ } ; do
        str=$str"$item\n"
    done
    echo -e $str > $hostapd_accept_file
    touch $hostapd_deny_file
fi


cat > $hostapd_config_file << EOF
interface=$interface
driver=nl80211

ssid2="$ssid"
utf8_ssid=1
country_code=$country_code
hw_mode=g
channel=$channel
preamble=1

macaddr_acl=$macaddr_acl
accept_mac_file=$hostapd_accept_file
deny_mac_file=$hostapd_deny_file
auth_algs=1
ignore_broadcast_ssid=0

ap_max_inactivity=86400
skip_inactivity_poll=0
disassoc_low_ack=1

#ieee80211n=1
#wme_enabled=1
#wmm_enabled=1

EOF

if [[ $wpa_passphrase != "" ]]; then
    cat >> $hostapd_config_file << EOF

wpa=2
wpa_passphrase=$wpa_passphrase
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
wpa_group_rekey=0
wpa_strict_rekey=0
wpa_gmk_rekey=0
wpa_ptk_rekey=0
EOF
fi

hostapd_res=1
if [[ $log == "yes" ]]; then
    hostapd $hostapd_config_file -P $hostapd_pid_file -t -dd &> $hostapd_log_file &
    hostapd_res=$?
else
    hostapd -B $hostapd_config_file -P $hostapd_pid_file &> /dev/null
    hostapd_res=$?
fi

if [[ $hostapd_res == 0 ]]; then
    exit_code=0
else
    exit_code=1
fi

exit $exit_code
