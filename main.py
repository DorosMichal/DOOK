import re
from stats import RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx
from config import statistics_list, 
"""
log format:
remote address
-
user name
date of request
"status line (GET )"
status
response length or '-'
"refer"
"user agent"
request time in microseconds
"""
statistics_list = [RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx] 


def format_str_to_re(format_str : str):
    def to_named_group(matchobj):
        return f"(?P<{matchobj.group(1)}>\[.+?\]|\".+?\"|\S+)"
    valid_letters = '[hlutrmUqHsBbfaTMDLp]'
    variables = "{[a-z\-]+}[ioe]"
    pattern = re.compile(rf'%\(({valid_letters}|{variables})\)s')
    return pattern.sub(to_named_group, format_str).replace('"', '\"')

def prepare_pattern(format_str : str):
    journal_pattern_str = r'\w{3} \d{2} \d{2}:\d{2}:\d{2} \S+ \S+: '
    pattern_str = format_str_to_re(format_str)
    return re.compile(journal_pattern_str + pattern_str)
  
def create_statistics_list()

     


def main(logfile, from_date, to_date):
    pattern = prepare_pattern()
    with open(logfile, 'r') as file:
        from_date, to_date = parse_date(from_date, to_date, next(file))
        create_statistics_list()
        check_requirements()
        for line in file:
            line = line.strip()
            date = find_date(line)
            if date < from_date:
                continue
            if date > to_date:
                break
            match = pattern.match(line)
            for stat in statistics_list:
                stat.update_stats(match)
    for stat in statistics_list:
        print(stat)

