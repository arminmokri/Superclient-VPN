#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --pid_file)
            pid_file="$2"
            shift # past argument
            shift # past value
            ;;
        --log_file)
            log_file="$2"
            shift # past argument
            shift # past value
            ;;
        --timeout)
            timeout="$2"
            shift # past argument
            shift # past value
            ;;
        --try_count)
            try_count="$2"
            shift # past argument
            shift # past value
            ;;
        --config_file)
            config_file="$2"
            shift # past argument
            shift # past value
            ;;
        --username)
            username="$2"
            shift # past argument
            shift # past value
            ;;
        --password)
            password="$2"
            shift # past argument
            shift # past value
            ;;
        --auth_file)
            auth_file="$2"
            shift # past argument
            shift # past value
            ;;
        --interface)
            interface="$2"
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

exit_code=1

cat > $auth_file << EOF
$username
$password
EOF

res_openvpn=1
n=0
until [ "$n" -ge $try_count ]
do
    echo -e "\n\nTry($n)\n\n"
    if [[ $log == "yes" ]]; then
        openvpn --config $config_file --dev $interface --auth-user-pass $auth_file --writepid $pid_file --log $log_file &
    else
        openvpn --config $config_file --dev $interface --auth-user-pass $auth_file --writepid $pid_file --log /dev/null &
    fi

    m=0
    until [ "$m" -ge $timeout ]
    do
        if [ -n "$(ip link show | grep $interface)" ]; then
            res_openvpn=0
            break
        fi
        m=$((m+1))
        sleep 1
    done

    if [ $res_openvpn == 0 ]; then
        break
    fi
    n=$((n+1))
    sleep 1
done

if [[ $res_openvpn == 0 ]]; then
    exit_code=0
else
    exit_code=1
fi

exit $exit_code
