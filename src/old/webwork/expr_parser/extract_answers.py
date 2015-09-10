#!/usr/bin/env python

import argparse
import os.path
import re
from webwork_parser import parse_webwork

def parse_pg_file(pg_file):
    answer_re = re.compile(".*\[_+\]{(.*)}")
    compute_re = re.compile("Compute\(\"(.*)\"\)")
    with open(os.path.expanduser(pg_file), 'r') as f:
        for line in f:
            m = answer_re.match(line)
            if m:
                print line
                print m.group(1)
                mc = compute_re.match(m.group(1))
                if mc:
                    print mc.group(1)
                    parsed = parse_webwork(mc.group(1))
                    print parsed
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract answers from a webwork PG file')
    parser.add_argument('pg_file')

    args = parser.parse_args()
    print args
    parse_pg_file(args.pg_file)
