#!/bin/bash

course=$1

source setup.sh
mkdir -p $MYSQL_DUMP_DIR
mkdir -p $WWAH_LOGS
mkdir -p $WWAH_PICKLE
mkdir -p $WWAH_OUTPUT
mkdir -p $WWAH_HINTS
./src/databases/backup_db.sh
# Process Past Answer Logs
past_log_txt="${course}_part_attempt.txt"
past_log_pkl="${course}_processed_logs_past_answer.pkl"
past_behavior_pkl="${course}_behavioral_statistics_past_answer.pkl"
./src/python/PastAnswerToRealtimeDump.py $course
./src/python/ProcessRealtimeMysqlDump.py $past_log_txt \
    $past_log_pkl
./src/python/BehaviourAnalysis.py $past_log_pkl $past_behavior_pkl
 Process Realtime Past Answer logs
realtime_log_txt="${MYSQL_DUMP_DIR}/${course}_realtime_past_answer.txt"
if [ -a "$realtime_log_txt" ]; then
    realtime_log_pkl="${course}_processed_logs_realtime.pkl"
    realtime_behavior_pkl="${course}_behavioral_statistics_realtime.pkl"
    ./src/python/ProcessRealtimeMysqlDump.py $realtime_log_txt $realtime_log_pkl
    ./src/python/BehaviourAnalysis.py $realtime_log_pkl $realtime_behavior_pkl
fi
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
