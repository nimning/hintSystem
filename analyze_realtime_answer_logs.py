#!/bin/bash

source setup_mysql_dump.sh
mkdir -p $FULL_DB_BACKUP_DIR
mkdir -p $WWAH_LOGS
mkdir -p $WWAH_PICKLE
mkdir -p $WWAH_OUTPUT
mkdir -p $WWAH_HINTS
./src/databases/backup_just_attempts.sh
./src/python/ProcessRealtimeMysqlDump.py
./src/python/BehaviourAnalysis.py
