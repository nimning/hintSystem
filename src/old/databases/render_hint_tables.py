#!/usr/bin/env python

import sys
from tornado.template import Template

if len(sys.argv) != 3:
    sys.stderr.write('usage: %s <hint_tables_template.sql> <course_name> \n'
        %sys.argv[0])
    exit(1)

# Render sql template with course_name set to the first command line argument
with open(sys.argv[1], 'r') as f:
    t = Template(f.read())
rendered = t.generate(course_name=sys.argv[2])
sys.stdout.write(rendered)
