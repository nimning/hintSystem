#!/usr/bin/env bash

pwd=`pwd`

export FULL_DB_BACKUP_DIR=${pwd}/data/db_backups
echo 'Directory where the full mysql backup is dumped' 
echo $WWAH_LOGS

export WWAH_LOGS=${pwd}/data/db_cse103_attempt_backups
echo 'Webwork logs directory $WWAH_LOGS=' 
echo $WWAH_LOGS

export WWAH_PG=/opt/webwork/courses/UCSD_CSE103/templates
echo 'Problem source files (def file pointing to .pg files) $WWAH_PG=' 
echo $WWAH_PG

export WWAH_PICKLE=${pwd}/data/realtime_past_answer_analysis
echo 'Pickle files containing processed information $WWAH_PICKLE=' 
echo $WWAH_PICKLE

export WWAH_OUTPUT=${pwd}/data/realtime_past_answer_analysis
echo 'Human readable output files$WWAH_OUTPUT=' 
echo $WWAH_OUTPUT

export WWAH_HINTS=${pwd}/data/Hints
echo 'Files edited by instructor to add hints $WWAH_HINTS=' 
echo $WWAH_HINTS

echo '------------------------------------'
export WWAH_SRC=${pwd}/src/python
echo 'mature python code: $WWAH_SRC=' 
echo $WWAH_SRC

export WWAH_NOTEBOOKS=${pwd}/src/notebooks
echo 'ipython notebooks $WWAH_NOTEBOOKS=' 
echo $WWAH_NOTEBOOKS

