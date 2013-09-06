import tornado.ioloop
import tornado.web
import tornado.gen
import logging
import pg_wrapper
import os

def task_checkanswer(pg_file, answers, seed, callback=None):
    callback(pg_wrapper.checkanswer(pg_file, answers, int(seed)))
 
class CheckAnswer(tornado.web.RequestHandler):
    """Check answers with PG"""
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """POST /checkanswer
        
        checkanswer makes a call to a perl script scripts/checkanswer.pl. More info [link].
        
        Inputs:
          pg_file: ...
          seed: ...
        Output:
          Answer dictionary descrbied in pg_wrapper.py
        """
        pg_file = self.get_argument("pg_file", default='', strip=False)
        seed = self.get_argument("seed", default='1', strip=False)

        # get AnSwEr*
        answers = {}
        for key in self.request.arguments:
            if key.startswith('AnSwEr'):
                answers[key] = self.request.arguments[key][0]
        
        if not os.path.isfile(pg_file):
            self.set_status(500)
            self.write("PG file not found\n")
            return
        
        if len(answers) == 0:
            self.set_status(500)
            self.write("No answers given\n")
            return
            
        results = yield tornado.gen.Task(task_checkanswer,
                                         pg_file, answers, int(seed))
        
        if results is None:
            self.set_status(500)
            self.write("Something went wrong\n")
            return
        
        self.write(results)
