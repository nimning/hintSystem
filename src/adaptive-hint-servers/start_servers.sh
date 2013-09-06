#!/bin/bash

zdaemon -p "python rest_server/rest_server.py" -d -s zdsock-rest start
zdaemon -p "python sockjs_server/sockjs_server.py" -d -s zdsock-sockjs start
