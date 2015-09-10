#!/bin/bash

PWD=`pwd`
BASEDIR=`dirname $PWD`
REST_DIR=$(echo $BASEDIR"/rest_server" | sed -e 's/\//\\\//g')
SOCKJS_DIR=$(echo $BASEDIR"/sockjs_server" | sed -e 's/\//\\\//g')

# SockJS servers
PORTS=( 4350 )
for PORT in "${PORTS[@]}"
do
    sed -e 's/SERVER_PATH=.*/SERVER_PATH='$SOCKJS_DIR'/' \
	-e 's/PORT=.*/PORT='$PORT'/' \
	hint-sockjs > /etc/init.d/hint-sockjs-$PORT
    chmod +x /etc/init.d/hint-sockjs-$PORT
done

# ReSTful servers
PORTS=( 7250 7251 7252 7253 7254 )
for PORT in "${PORTS[@]}"
do
    sed -e 's/SERVER_PATH=.*/SERVER_PATH='$REST_DIR'/' \
	-e 's/PORT=.*/PORT='$PORT'/' \
	hint-rest > /etc/init.d/hint-rest-$PORT
    chmod +x /etc/init.d/hint-rest-$PORT
done
