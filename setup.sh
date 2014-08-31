#!/usr/bin/env bash

pwd=`pwd`

export MYSQL_DUMP_DIR=${pwd}/data/db_backups
echo 'Directory where the full mysql backup is dumped' 
echo $WWAH_LOGS

export WWAH_LOGS=${pwd}/data/cse103_original_data/WebWork/logs
echo 'Webwork logs directory $WWAH_LOGS=' 
echo $WWAH_LOGS

#export WWAH_PG=${pwd}/data/course_webwork_data #Past year's data
export WWAH_PG=${pwd}/opt/webwork/courses/UCSD_CSE103/templates
echo 'Problem source files (def file pointing to .pg files) $WWAH_PG=' 
echo $WWAH_PG

export WWAH_PICKLE=/Users/yoavfreund/Google\ Drive/PickleFiles    #${pwd}/data/PickleFiles
echo 'Pickle files containing processed information $WWAH_PICKLE=' 
echo $WWAH_PICKLE

export WWAH_OUTPUT=${pwd}/data/OutputFiles
echo 'Human readable output files$WWAH_OUTPUT=' 
echo $WWAH_OUTPUT

export WWAH_HINTS=${pwd}/data/Hints
echo 'Files edited by instructor to add hints $WWAH_HINTS=' 
echo $WWAH_HINTS

echo '------------------------------------'
export WWAH_SRC=${pwd}/src
echo 'mature python code: $WWAH_SRC=' 
echo $WWAH_SRC

export WWAH_NOTEBOOKS=${pwd}/src/notebooks
echo 'ipython notebooks $WWAH_NOTEBOOKS=' 
echo $WWAH_NOTEBOOKS




