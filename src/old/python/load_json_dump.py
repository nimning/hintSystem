import json
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Load problem data JSON dump')
parser.add_argument('-f', '--filename', help='file to load')
parser.add_argument('-t', '--table', help='table to load',
                    default='past_answers')
args = parser.parse_args()

with open(args.filename, 'r') as f:
    data = json.load(f)
    df = pd.DataFrame(data[args.table])

print df
