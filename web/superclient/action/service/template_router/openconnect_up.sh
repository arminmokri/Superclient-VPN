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
        --protocol)
            protocol="$2"
            shift # past argument
            shift # past value
            ;;
        --gateway)
            gateway="$2"
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
        --interface)
            interface="$2"
            shift # past argument
            shift # past value
            ;;
        --no_dtls)
            no_dtls="yes"
            shift # past argument
            ;;
        --passtos)
            passtos="yes"
            shift # past argument
            ;;
        --no_deflate)
            no_deflate="yes"
            shift # past argument
            ;;
        --deflate)
            deflate="yes"
            shift # past argument
            ;;
        --no_http_keepalive)
            no_http_keepalive="yes"
            shift # past argument
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

# no_dtls
if [ "$no_dtls" == "yes" ]; then
    no_dtls="--no-dtls"
else
    no_dtls=""
fi
# passtos
if [ "$passtos" == "yes" ]; then
    passtos="--passtos"
else
    passtos=""
fi
# no_deflate
if [ "$no_deflate" == "yes" ]; then
    no_deflate="--no-deflate"
else
    no_deflate=""
fi
# deflate
if [ "$deflate" == "yes" ]; then
    deflate="--deflate"
else
    deflate=""
fi
# no_http_keepalive
if [ "$no_http_keepalive" == "yes" ]; then
    no_http_keepalive="--no-http-keepalive"
else
    no_http_keepalive=""
fi

exit_code=1

tmpfile1=$(mktemp)
tmpfile2=$(mktemp)
trap 'rm -f $tmpfile1 $tmpfile2' EXIT

#$(timeout $timeout openssl s_client -connect $gateway </dev/null 2>/dev/null | openssl x509 -text > $tmpfile1)
#res1=$?
res1=0
$(timeout $timeout openssl s_client -showcerts -connect $gateway </dev/null 2>/dev/null | openssl x509 -outform PEM > $tmpfile2)
res2=$?
if [ $res1 == 0 ] && [ $res2 == 0 ]; then
    servercert=$(openssl x509 -in $tmpfile2 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64)
    servercert="pin-sha256:"$servercert
    n=0
    until [ "$n" -ge $try_count ]
    do
        echo -e "\n\nTry($n)\n\n"
        if [[ $log == "yes" ]]; then
            timeout $timeout echo $password | \
            openconnect --reconnect-timeout=30 --background --passwd-on-stdin \
            $no_dtls $passtos $no_deflate $deflate $no_http_keepalive \
            --protocol=$protocol --interface=$interface --pid-file=$pid_file  $gateway --user=$username  --servercert $servercert &> $log_file
        else
            timeout $timeout echo $password | \
            openconnect --reconnect-timeout=30 --background --passwd-on-stdin \
            $no_dtls $passtos $no_deflate $deflate $no_http_keepalive \
            --protocol=$protocol --interface=$interface --pid-file=$pid_file  $gateway --user=$username  --servercert $servercert &> /dev/null
        fi
        exit_code=$?
        if [ $exit_code == 0 ]; then
            break
        fi
        n=$((n+1))
        sleep 1
    done
else
    exit_code=10
fi

#if [ $exit_code == 0 ]; then
#fi

exit $exit_code
