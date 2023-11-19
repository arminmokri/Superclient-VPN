#!/bin/bash

id=$1
gateway=$2
username=$3
password=$4
priority=$5

nmcli connection add connection.type vpn connection.id $id connection.autoconnect false vpn.service-type openconnect \
vpn.data " \
authtype=password, \
autoconnect-flags=2, \
certsigs-flags=2, \
cookie-flags=2, \
enable_csd_trojan=no, \
gateway=$gateway, \
gateway-flags=2, \
gwcert-flags=2, \
lasthost-flags=2, \
pem_passphrase_fsid=yes, \
prevent_invalid_cert=no, \
protocol=anyconnect, \
resolve-flags=2, \
stoken_source=disabled, \
xmlconfig-flags=2, \
service-type=openconnect" \
vpn.secrets " \
username=$username, \
password=$password, \
priority=$priority, \
success=0, \
failed=0" \
ipv4.method auto \
ipv6.method auto

echo $?
