import tornado.ioloop
import tornado.web
import logging
import argparse

from render import Render
from checkanswer import CheckAnswer
from webwork import (ProblemSeed, ProblemPGPath, ProblemPGFile,
                     RealtimeUserProblemAnswers, RealtimeProblemAnswer,
                     SetIds, Sets, Problems, ExportProblemData, AnswersByPart)
from hints_api import (UserProblemHints, Hint, AssignedHint,
                       ProblemHints, HintFeedback, RunHintFilters,
                       HintFilter, AssignedHintFilter)

from auth import (Login)
from parsers import ParseString
# Server configuration
BIND_IP = '0.0.0.0'
DEFAULT_PORT = 4351
LOG_PATH = '/var/log/hint'

application = tornado.web.Application([
    (r"/render", Render),
    (r"/checkanswer", CheckAnswer),
    (r"/problem_seed", ProblemSeed),
    (r"/pg_path", ProblemPGPath),
    (r"/pg_file", ProblemPGFile),
    (r"/user_problem_hints", UserProblemHints),
    (r"/hint", Hint),
    (r"/assigned_hint", AssignedHint),
    (r"/realtime_user_problem_answers", RealtimeUserProblemAnswers),
    (r"/problem_hints", ProblemHints),
    (r"/realtime_problem_answer", RealtimeProblemAnswer),
    (r"/hint_feedback", HintFeedback),
    (r"/run_hint_filters", RunHintFilters),
    (r"/hint_filter", HintFilter),
    (r"/assigned_hint_filter", AssignedHintFilter),
    (r"/set_ids", SetIds),
    (r"/sets", Sets),
    (r"/problems", Problems),
    (r"/login", Login),
    (r"/answers_by_part", AnswersByPart),
    (r"/parse_string", ParseString),
    (r"/export_problem_data", ExportProblemData),
    ], gzip=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
                        type=int,
                        default=DEFAULT_PORT,
                        help="port to listen")
    args = parser.parse_args()

    # set up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                  '%(levelname)s - %(message)s')

    log_filename =  LOG_PATH + "/rest-%d.log"%args.port
    handler = logging.handlers.RotatingFileHandler(log_filename,
                                                   maxBytes=2000000,
                                                   backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
   
    application.listen(args.port, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,args.port))
    
    tornado.ioloop.IOLoop.instance().start()
