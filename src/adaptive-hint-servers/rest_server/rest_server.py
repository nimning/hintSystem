import tornado.ioloop
import tornado.web
import logging

from render import Render 
from checkanswer import CheckAnswer
from webwork import ProblemSeed, ProblemPGPath, ProblemPGFile, UserProblemAnswers, RealtimeProblemAnswer
from hints_api import UserProblemHints, Hint, AssignedHint, HintAnswer, \
    ProblemHints

# Server configuration
BIND_IP = '0.0.0.0'
DEFAULT_PORT = 4351
    
application = tornado.web.Application([
    (r"/render", Render),
    (r"/checkanswer", CheckAnswer),
    (r"/problem_seed", ProblemSeed),
    (r"/pg_path", ProblemPGPath),
    (r"/pg_file", ProblemPGFile),
    (r"/user_problem_hints", UserProblemHints),
    (r"/hint", Hint),
    (r"/assigned_hint", AssignedHint),
    (r"/user_problem_answers", UserProblemAnswers),
    (r"/problem_hints", ProblemHints),
    (r"/realtime_problem_answer", RealtimeProblemAnswer),
    (r"/hint_answer", HintAnswer)
    ])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
                        type=int,
                        default=DEFAULT_PORT,
                        help="port to listen")
    args = parser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)

    application.listen(args.port, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,args.port))
    
    tornado.ioloop.IOLoop.instance().start()
