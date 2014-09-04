#!/bin/sh

newgrp wwdata
umask 2
cd /opt/webwork/courses
/opt/webwork/webwork2/bin/addcourse admin --db-layout=sql_single --users=adminClasslist.lst --professors=admin
exit
