#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
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

# hotspotConfig
if [ -n "$(pgrep -f 'hostapd')" ]; then
    killall 'hostapd' &>/dev/null
    sleep 1
fi

if [ -f "$hostapd_config_file" ]; then
    rm $hostapd_config_file
fi
if [ -f "$hostapd_pid_file" ]; then
    rm $hostapd_pid_file
fi
if [ -f "$hostapd_log_file" ]; then
    rm $hostapd_log_file
fi
if [ -f "$hostapd_accept_file" ]; then
    rm $hostapd_accept_file
fi
if [ -f "$hostapd_deny_file" ]; then
    rm $hostapd_deny_file
fi

exit $exit_code
