#!/bin/bash


STATUS=`ps ax | grep -v grep | grep "rest_server.py --port="$1`
E_SUCCESS="0"
E_WARNING="1"
E_CRITICAL="2"
E_UNKNOWN="3"

if [ "$STATUS" ] 
then
        echo "OK - ReSt($1) working"
        exit ${E_SUCCESS}
else
        echo "CRITICAL - ReST($1) not working"
        exit ${E_CRITICAL}
fi
