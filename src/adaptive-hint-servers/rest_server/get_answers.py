from pg_wrapper import checkanswer

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pg_file')
    parser.add_argument('seed')
    args = parser.parse_args()

    answers = checkanswer(args.pg_file, {}, args.seed)
    for key, val in answers.iteritems():
        print key, val['correct_value']
