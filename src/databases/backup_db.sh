#!/bin/bash

echo """ 
################################################################################
Make sure to cd <adaptive hints root> and source setup_mysql_dump.sh to get
    the directory to back up to

If you get a 'Can't create/write to file...' error with running backups, add:
  ${MYSQL_DUMP_DIR} r,
  ${MYSQL_DUMP_DIR}/* rw,

to 

/usr/sbin/mysqld {} in /etc/apparmor.d/usr.sbin.mysqld

then run

/etc/init.d/apparmor reload

See stack overflow response http://stackoverflow.com/a/2986764

Also chmod 777 ${MYSQL_DUMP_DIR}
################################################################################
"""

# Backup all webwork tables to $BACKUP_DIR
sudo mysqldump -u root -T $MYSQL_DUMP_DIR -p webwork
