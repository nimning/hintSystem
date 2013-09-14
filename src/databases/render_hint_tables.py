import sys
from tornado.template import Template

if len(sys.argv) != 2:
    sys.stderr.write('usage: %s <course_name>\n')
    exit(1)

# Render sql template with course_name set to the first command line argument
t = Template(sys.stdin.read())
rendered = t.generate(course_name=sys.argv[1])
sys.stdout.write(rendered)
