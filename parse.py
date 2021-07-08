import argparse
from config import statistics_class_list, format_str
from main import main

parser = argparse.ArgumentParser()
parser.add_argument("logfile", help="name of the file with logs", type=str)
parser.add_argument("--from", default=None, dest="_from", help="date to start (inclusive) in format dd-mm-yyyy_hh-mm-ss", type=str)
parser.add_argument("--to", default=None, dest="_to", help="date of stop (inclusive) in format dd-mm-yyyy_hh-mm-ss", type=str)

args = parser.parse_args()

if __name__ == "__main__":
    main(args.logfile, args._from, args._to, format_str, statistics_class_list)