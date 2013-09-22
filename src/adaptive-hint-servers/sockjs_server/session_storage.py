import datetime as dt

class SessionStorage(object):
    """Session data storage

    Storage for maintaining session data. In a typical SockJS setup,
    when a client is disconnected, the data is lost. The client can
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

    def is_timedout(self, session_id):
        self._remove_expired_sessions()
        return not (session_id in self.sessions)

    def all_sessions(self):
        """List of all session data"""
        sessions = []
        for session_id in data:
            for hashkey in data[session_id]:
                sessions.append(data[session_id][hashkey])
        return sessions

    def load(self, session_id, hashkey):
        """Load a saved session

        Arguments
        ---------
          session_id : string
            Webwork session ID
          hashkey : hashable
            Suggested hashkey is (course_id, set_id, problem_id)

        Return
        ------
          The previously saved session data or None
          if the session was not saved earlier.          
        """
        try:
            # renew the timeout
            self.sessions[session_id] = (dt.datetime.now() +
                                         dt.timedelta(minutes=self.timeout))

            t = self.data[session_id][hashkey]
            return t
        except KeyError:
            return None

    def save(self, session_id, hashkey, session):
        """Save a session

        Arguments
        ---------
          session_id : string
            Webwork session ID
          hashkey : hashable
            Suggested hashkey is (course_id, set_id, problem_id)
          session : object
            Session data to save
        """
        if session is not None:
            if session_id not in self.data:
                self.data[session_id] = {}

            # renew the timeout
            self.sessions[session_id] = (dt.datetime.now() +
                                         dt.timedelta(minutes=self.timeout))
            
            self.data[session_id][hashkey] = session

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
    storage.save(1, (1, 1, 1), 'ans1')
    storage.save(1, (1, 1, 2), 'ans2')
    print storage.load(1, (1, 1, 1))
    print storage.load(1, (1, 1, 2))
    print storage.load(1, (1, 1, 3))
    import time
    time.sleep(1.1)
    print storage.data
    print storage.sessions
    storage._remove_expired_sessions()
    print storage.data
    print storage.sessions
    
if __name__ == "__main__":
    _test()
