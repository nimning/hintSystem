#!/bin/bash

# SockJS servers
PORTS=( 4350 )
for PORT in "${PORTS[@]}"
do
    sudo service hint-sockjs-$PORT restart
done

# ReSTful servers
PORTS=( 7250 7251 7252 7253 7254 )
for PORT in "${PORTS[@]}"
do
    sudo service hint-rest-$PORT restart
done
