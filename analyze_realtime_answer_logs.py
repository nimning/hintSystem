#!/bin/bash

source setup_mysql_dump.sh
./src/databases/backup_just_attempts.sh
./src/python/ProcessRealtimeMysqlDump.py
./src/python/BehaviourAnalysis.py
