from tzlocal import get_localzone
import time
from datetime import datetime
import pytz

# MySQLDb returns utc timestamps without associated timezones
def utc_to_system_timestamp(dt):
    ''' Assume the given datetime object (without associated tzinfo)
        is in utc.  Return it converted to the local system time.  '''

    dt = dt.replace(tzinfo = pytz.utc)
    local_datetime = dt.astimezone(get_localzone())
    return int( local_datetime.strftime('%s') )

