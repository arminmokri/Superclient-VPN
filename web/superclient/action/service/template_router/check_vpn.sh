#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --method)
            method="$2"
            shift # past argument
            shift # past value
            ;;
        --domain)
            domain="$2"
            shift # past argument
            shift # past value
            ;;
        --timeout)
            timeout="$2"
            shift # past argument
            shift # past value
            ;;
        --retry)
            retry="$2"
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
if [[ $method == "curl" ]]; then
    n=0
    until [ "$n" -ge $retry ]
    do
        echo "Try($n)"
        timeout $timeout curl $domain
        exit_code=$?
        if [ $exit_code == 0 ]; then
            break
        fi
        n=$((n+1)) 
        sleep 1
    done

elif [[ $method == "ping" ]]; then
    n=0
    until [ "$n" -ge $retry ]
    do
        echo "Try($n)"
        ping -c 1 -W $timeout $domain
        exit_code=$?
        if [ $exit_code == 0 ]; then
            break
        fi
        n=$((n+1)) 
        sleep 1
    done
fi

exit $exit_code
