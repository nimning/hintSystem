#!/bin/bash
echo "Updating hint tables for $1"
./render_hint_tables.py add_trigger_cond.sql $1 | mysql webwork -u webworkWrite -p
./render_hint_tables.py add_part_id_to_hints.sql $1 | mysql webwork -u webworkWrite -p

