#!/bin/bash
echo "Creating hint tables for $1"
./render_hint_tables.py hint_tables_template.sql $1 | mysql webwork
./render_hint_tables.py hint_filter_template.sql $1 | mysql webwork
./render_hint_tables.py realtime_answers_template.sql $1 | mysql webwork
./render_hint_tables.py test_hint_tables_template.sql $1 | mysql webwork
