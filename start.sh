#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <host ip address> <android ip addr>"
    exit 1
fi

function ctrl_c() {
    echo "Stopping..."
    pid=`ps -au | grep "objection -N -g com.immediasemi.android.blink" | tr -s ' ' | cut -d ' ' -f2 | head -n1`
    kill -9 $pid
    exit 1
}

trap ctrl_c INT

# generate self-signed SSL certificate
if [ ! -d "ssl" ]; then
    mkdir ssl
    openssl genrsa -out ssl/server.key 2048
    openssl req -new -key ssl/server.key -x509 -days 3653 -out ssl/server.crt
    cat ssl/server.key ssl/server.crt > ssl/server.pem
fi

# set android proxy
adb shell settings put global http_proxy $1:8080
adb shell settings put global global_http_proxy_host $1
adb shell settings put global global_http_proxy_port 8080

# start new blink process with objection api
frida-kill -H $2 Blink
objection -N -g com.immediasemi.android.blink -h $2 api &

# wait for objection to load
while true; do
    curl -s -f http://127.0.0.1:8888/rpc/invoke/test &>/dev/null
    if [ "$?" -eq 0 ]; then
        break
    fi 
    sleep 1
done

# disable ssl pinning and load mbedtls_x509_crt_verify_with_profile hook
curl -s -X POST "http://127.0.0.1:8888/rpc/invoke/androidSslPinningDisable" -H "Content-Type: application/json" -d '{"quiet": false}' &>/dev/null
python inject-tls-verify-hook.py $2 &

# start mitmproxy
mitmdump -q --set tcp_bind_ip=$1 -s proxy.py
