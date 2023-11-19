#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
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

########################################################################
# start dns
########################################################################

# make dns str
str="#MYDNS_START\n"
for item in ${dns_server//,/ } ; do
    str=$str"nameserver $item\n"
done
str=$str"#MYDNS_END"

# add new dns
resolvconf_path="/etc/resolvconf/resolv.conf.d/head"
echo -e "$str\n$(cat $resolvconf_path)" > $resolvconf_path
resolvconf -u

exit $exit_code
