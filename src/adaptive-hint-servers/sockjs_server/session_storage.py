import datetime as dt

class SessionStorage(object):
    """Session data storage

    Storage for maintaining session data. In a typical SockJS setup,
    when a client is disconnected, the data is lost. The clients can
    use this class as a storage and retrieve the stored data when they
    reconnect with the server.

    Attributes
    ----------
      timeout : int
        Session timeout in minutes (Default: 10)
        
    """
    def __init__(self, timeout=10):
        self.data = {}
        self.sessions = {}
        self.timeout = timeout
        
    def load(self, varname, session_id, course_id, set_id, problem_id):
        """Load a saved variable

        Arguments
        ---------
          varname : string
            Variable name
          session_id : string
            Webwork session ID
          course_id : string
            Webwork course ID
          set_id : string
            Webwork set ID
          problem_id : string
            Webwork problem ID

        Return
        ------
          The previusly saved value of the variable or None
          if the variable was not saved earlier.

        """
        try:
            # renew the timeout
            self.sessions[session_id] = (dt.datetime.now() +
                                         dt.timedelta(minutes=self.timeout))

            t = self.data[session_id][(course_id, set_id, problem_id)][varname]
            return t
        except KeyError:
            return None

    def save(self, varname, session_id, course_id, set_id, problem_id, value):
        """Save a variable

        Arguments
        ---------
          varname : string
            Variable name
          session_id : string
            Webwork session ID
          course_id : string
            Webwork course ID
          set_id : string
            Webwork set ID
          problem_id : string
            Webwork problem ID
          value : object
            The value of the variable
        """
        if value is not None:
            if session_id not in self.data:
                self.data[session_id] = {}

            # renew the timeout
            self.sessions[session_id] = (dt.datetime.now() +
                                         dt.timedelta(minutes=self.timeout))

            key = (course_id, set_id, problem_id)
            if key not in self.data[session_id]:
                self.data[session_id][key] = {}
            
            self.data[session_id][key][varname] = value

        # Also check for and remove timed-out sessions
        self._remove_expired_sessions()

    def _remove_expired_sessions(self):
        now = dt.datetime.now()
        for session_id in self.sessions.keys():
            if self.sessions[session_id] < now:
                del self.data[session_id]
                del self.sessions[session_id]

def _test():
    storage = SessionStorage(timeout=1.0/60)
    storage.save('answers', 1, 1, 1, 1, 'ans1')
    storage.save('answers', 1, 1, 1, 2, 'ans2')
    print storage.load('answers', 1, 1, 1, 1)
    print storage.load('answers', 1, 1, 1, 2)
    print storage.load('answers', 1, 1, 1, 3)
    import time
    time.sleep(1.1)
    print storage.data
    print storage.sessions
    storage._remove_expired_sessions()
    print storage.data
    print storage.sessions
    
if __name__ == "__main__":
    _test()
