#!/bin/bash

source setup.sh
mkdir -p $MYSQL_DUMP_DIR
mkdir -p $WWAH_LOGS
mkdir -p $WWAH_PICKLE
mkdir -p $WWAH_OUTPUT
mkdir -p $WWAH_HINTS
#./src/databases/backup_just_attempts.sh
# Process Past Answer Logs
./src/python/PastAnswerToRealtimeDump.py
./src/python/ProcessRealtimeMysqlDump.py UCSD_CSE103_part_attempt.txt \
    ProcessedLogsPastAnswer.pkl
./src/python/BehaviourAnalysis.py ProcessedLogsPastAnswer.pkl BehavioralStatisticsPastAnswer.pkl
# Process Realtime Past Answer logs
#./src/python/ProcessRealtimeMysqlDump.py UCSD_CSE103_realtime_past_answer.txt \
#    ProcessedLogsRealtime.pkl
#./src/python/BehaviourAnalysis.py ProcessedLogsRealtime.pkl BehavioralStatisticsRealtime.pkl
