#!/bin/bash

get_iface_type () {
    local IF=$1 TYPE
    test -n "$IF" || return 1
    test -d /sys/class/net/$IF || return 2
    case "`cat /sys/class/net/$IF/type`" in
            1)
                TYPE=eth
                # Ethernet, may also be wireless, ...
                if test -d /sys/class/net/$IF/wireless -o \
                        -L /sys/class/net/$IF/phy80211 ; then
                    TYPE=wlan
                elif test -d /sys/class/net/$IF/bridge ; then
                    TYPE=bridge
                elif test -f /proc/net/vlan/$IF ; then
                    TYPE=vlan
                elif test -d /sys/class/net/$IF/bonding ; then
                    TYPE=bond
                elif test -f /sys/class/net/$IF/tun_flags ; then
                    TYPE=tap
                elif test -d /sys/devices/virtual/net/$IF ; then
                    case $IF in
                      (dummy*) TYPE=dummy ;;
                    esac
                fi
                ;;
           24)  TYPE=eth ;; # firewire ;; # IEEE 1394 IPv4 - RFC 2734
           32)  # InfiniBand
            if test -d /sys/class/net/$IF/bonding ; then
                TYPE=bond
            elif test -d /sys/class/net/$IF/create_child ; then
                TYPE=ib
            else
                TYPE=ibchild
            fi
                ;;
          512)  TYPE=ppp ;;
          768)  TYPE=ipip ;; # IPIP tunnel
          769)  TYPE=ip6tnl ;; # IP6IP6 tunnel
          772)  TYPE=lo ;;
          776)  TYPE=sit ;; # sit0 device - IPv6-in-IPv4
          778)  TYPE=gre ;; # GRE over IP
          783)  TYPE=irda ;; # Linux-IrDA
          801)  TYPE=wlan_aux ;;
        65534)  TYPE=tun ;;
    esac
    # The following case statement still has to be replaced by something
    # which does not rely on the interface names.
    case $IF in
        ippp*|isdn*) TYPE=isdn;;
        mip6mnha*)   TYPE=mip6mnha;;
    esac
    test -n "$TYPE" && echo $TYPE && return 0
    return 3
}

devs=$1

for dev in $(ls /sys/class/net); do
    if [[ "$devs" == $(get_iface_type $dev) ]]; then
        echo $dev
    fi
done
