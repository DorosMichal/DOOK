import re
from datetime import datetime

def format_str_to_re(format_str : str):
    format_str = format_str.replace(r'"', '')
    def to_named_group(matchobj):
        return f"(?P<{matchobj[1]}>(\[.+?\])|(\".+?\")|\S+)"
    valid_letters = '[hlutrmUqHsBbfaTMDLp]'
    variables = "{[a-z\-]+}[ioe]"
    pattern = re.compile(rf'%\(({valid_letters}|{variables})\)s')
    return pattern.sub(to_named_group, format_str).replace(r'"', r'\"')

def prepare_pattern(format_str : str):
    journal_pattern_str = r'\w{3} \d{2} \d{2}:\d{2}:\d{2} \S+ \S+: '
    pattern_str = format_str_to_re(format_str)
    return re.compile(journal_pattern_str + pattern_str)
  
def requirements_satisfied(stat, format_str : str):
    for req in stat.requirements:
        if f'%({req})s' not in format_str:
            print(f"required {req} field for statistic {stat.__name__} was not found in format string, hence this statistic won't be displayed")
            return False
    return True

def get_date_from_match(matchobj : re.Match):
    """takes match-object, if it contains date it converts it to datetime object"""
    date_format_str = "[%d/%b/%Y:%H:%M:%S" ##without timezone
    try:
        date_str = matchobj['t'][:-7]
    except IndexError:
        print("couldn't find date in logs, while --from or --to arguments provided, add date to logs ( \%(t)s ) or print statistics for all logs")
        exit(1)
    return datetime.strptime(date_str, date_format_str)

def get_date_from_header(header : str, start : bool):
    """takes journalctl header, if start = True, returns starting date, else ending"""
    date_format_str = "%Y-%m-%d %H:%M:%S"
    date_str = ("begin" if start else "end") + r" at \w{3} (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} 
    match = re.search(date_str, header)
    return datetime.strptime(match[1], date_format_str)

def parse_dates(from_date : str, to_date : str, header : str):
    """takes from and to date as strings and log file header,
    returns datetime objects - first and last date,
    and all - boolean informing if all logs in file are considered"""
    date_str = '%d-%m-%Y_%H-%M-%S'
    all = from_date is None and to_date is None
    from_date = datetime.strptime(from_date, date_str) if from_date is not None else get_date_from_header(header, 1)
    to_date = datetime.strptime(to_date, date_str) if to_date is not None else get_date_from_header(header, 0)
    return from_date, to_date, all


def main(logfile, from_date, to_date, format_str, statistics_class_list):
    pattern = prepare_pattern(format_str)
    with open(logfile, 'r') as file:
        from_date, to_date, all = parse_dates(from_date, to_date, next(file))
        statistics_list = [stat(from_date, to_date) for stat in statistics_class_list if requirements_satisfied(stat, format_str)]
        for i, line in enumerate(file):
            line = line.strip()
            match = pattern.match(line)
            if match is None:
                print(f"couldn't match log format in line {i}")
                continue
            if not all:
                date = get_date_from_match(match)
                if date < from_date:
                    continue
                if date > to_date:
                    break
            for stat in statistics_list:
                stat.update_stats(match)
    for stat in statistics_list:
        print(stat)

