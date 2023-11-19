#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --default_gateway_mode)
            default_gateway_mode="$2"
            shift # past argument
            shift # past value
            ;;
        --default_gateway)
            default_gateway="$2"
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

# default_gateway
if [[ $default_gateway_mode == "manual" ]]; then
    n=0
    until [ "$n" -ge 60 ]
    do
        route add default gw $default_gateway
        res=$?
        if [ $res == 0 ]; then
            break
        fi
        n=$((n+1)) 
        sleep 1
    done
fi

exit $exit_code
