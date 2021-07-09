import re
from datetime import datetime

def format_str_to_re(format_str : str):
    """convert format string to regular expression with properly named groups"""
    def eliminate_quotes(matchobj):
        return matchobj[1]

    def to_named_group(matchobj):
        """group should match 3 scenarios
            1) [anything]
            2) "anything"
            3) one word (any characters but without white spaces)
            """
        return f"(?P<{matchobj[1]}>(\[.+?\])|(\".+?\")|\S+)"

    # get rid of quotes in format_str, to not match them twice
    # finds all quoted formats "{variable_name}one_letter" where {variable_name} is optional
    quotes_pattern = r'\"(%\(({.+?})?\w\)s)\"'
    format_str = re.sub(quotes_pattern, eliminate_quotes, format_str)
    
    valid_letters = "[hlutrmUqHsBbfaTMDLp]"
    variables = "{[a-z\-]+}[ioe]"
    pattern = re.compile(rf'%\(({valid_letters}|{variables})\)s')
    #replace access_log_format with corresponding regex and escape quotes (to match them directly)
    return pattern.sub(to_named_group, format_str).replace('"', r'\"')

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
    date_format_str = "[%d/%b/%Y:%H:%M:%S" ## without timezone
    try:
        date_str = matchobj['t'][:-7]
    except IndexError:
        print(r"couldn't find date in logs, while --from or --to arguments provided, add date to logs ( \%(t)s ) or print statistics for all logs")
        exit(1)
    return datetime.strptime(date_str, date_format_str)

def get_date_from_file(file, start : bool, pattern : re.Pattern):
    line = ''
    if start: #first(oldest) log is at the end of file
        for line in file:
            pass
    else:
        line = next(file)
 
    line.strip()
    if line == '':
        print("file contains no logs")
        exit(1)
    match = pattern.match(line)
    if match is None:
        print("couldn't match log format")
        exit(1)
    
    file.seek(0) #get file back to the correct possition
    next(file)
    return get_date_from_match(match)

def parse_date(date : str, start : bool, file, pattern : re.Pattern):
    """takes date as string, bool informing that its --from date when true, --to date otherwise,
    file and line pattern
    returns datetime objects - when start is True either converted date or date of first log, whichever comes later
    analogously when start is False either converted date or date of last log, whichever comes first.
    """
    date_str = '%d-%m-%Y_%H-%M-%S'
    file_date = get_date_from_file(file, start, pattern)
    try:
        date = datetime.strptime(date, date_str) if date is not None else file_date
    except ValueError:
        print(f"{'--from' if start else '--to'} date provided does not match requested format: {date_str}")
        exit(1)
    return max(date, file_date) if start else min(date, file_date)


def main(logfile, from_date, to_date, format_str, statistics_class_list):
    pattern = prepare_pattern(format_str)
    with open(logfile, 'r') as file:
        next(file) #skip header
        all = from_date is None and to_date is None
        from_date = parse_date(from_date, True, file, pattern)
        to_date = parse_date(to_date, False, file, pattern)
        statistics_list = [stat(from_date, to_date) for stat in statistics_class_list if requirements_satisfied(stat, format_str)]
        for i, line in enumerate(file):
            line = line.strip()
            match = pattern.match(line)
            if match is None:
                print(f"couldn't match log format in line {i}")
                continue
            if not all:
                date = get_date_from_match(match)
                if date > to_date:
                    continue
                if date < from_date:
                    break
            for stat in statistics_list:
                stat.update_stats(match)
    for stat in statistics_list:
        print(stat)

