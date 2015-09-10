#!/bin/bash

# Set environment variables
source /opt/Webwork_AdaptiveHints/setup.sh
# temporary output file
TEMPF=$(mktemp pa_script_XXXXXXXX)
python /opt/Webwork_AdaptiveHints/src/python/past_answer_to_answers_by_part.py -c CSE103_Fall14 > $TEMPF


