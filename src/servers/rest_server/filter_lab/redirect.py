import sys
import StringIO

print 'before redirect'
old_stdout=sys.stdout
sys.stdout=StringIO.StringIO()
print 'after redirect'
text=sys.stdout.getvalue()
sys.stdout=old_stdout
print 'text=',text