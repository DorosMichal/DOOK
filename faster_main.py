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

def prepare_pattern_fast():
    ###test function
    pat = r'\w{3} \d{2} \d{2}:\d{2}:\d{2} \S+ \S+: [\d\.]{7,15} \- \S+\
         (?P<t>\[\S{20} \S{5}]) \".+?\" (?P<s>\d{3}) (?P<b>\d+) \".+?\" \"\S+?\" (?P<D>\d+)'
    return re.compile(pat)

def requirements_satisfied(stat, format_str : str):
    for req in stat.requirements:
        if f'%({req})s' not in format_str:
            print(f"required {req} field for statistic {stat.__name__}\
             was not found in format string, hence this statistic won't be displayed")
            return False
    return True

def get_date_from_match(matchobj : re.Match):
    """takes match-object, if it contains date it converts it to datetime object"""
    date_format_str = "[%d/%b/%Y:%H:%M:%S" ## without timezone
    try:
        date_str = matchobj['t'][:-7]
    except IndexError:
        print(r"couldn't find date in logs, while --from or --to arguments provided,\
             add date to logs ( \%(t)s ) or print statistics for all logs")
        exit(1)
    return datetime.strptime(date_str, date_format_str)

def get_date_from_file(file, start : bool, pattern : re.Pattern):
    """assumes file starts with header"""
    next(file)
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
    return get_date_from_match(match)

def get_correct_date(date : str, start : bool, file, pattern : re.Pattern):
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

def get_date_from_line_number(number : int, offsets, file, pattern : re.Pattern):
    file.seek(offsets[number])
    line = file.readline()
    match = pattern.match(line)
    return get_date_from_match(match)

def fill_offsets(file):
    offset = 0
    t = [0]
    for line in file:
        offset += len(line)
        t.append(offset)
    file.seek(0)
    return t

def LastNotGreater(last_date, offsets, file, pattern):
    left, right = 1, len(offsets) - 2 ##pierwsza linijka z datą jest pod indeksem 1, ostatnia pod dl - 2
    ##if t[left] > x: return -1 nie ma takiego przypadku
    while(left < right):
        m = left + (right-left)//2
        if get_date_from_line_number(m, offsets, file, pattern) > last_date:
            left = m + 1
        else: 
            right = m
    return left

def FirstNotSmaller(first_date, offsets, file, pattern):
    left, right = 1, len(offsets) - 2
    while(left < right):
        m = left + (right-left+1)//2
        if get_date_from_line_number(m, offsets, file, pattern) < first_date:
            right = m - 1
        else:
            left = m
    return left

def main(logfile, from_date, to_date, format_str, statistics_class_list):
    pattern = prepare_pattern(format_str)
    try:
        with open(logfile, 'r') as file:            
            from_date = get_correct_date(from_date, True, file, pattern)
            to_date = get_correct_date(to_date, False, file, pattern)

            statistics_list = [stat(from_date, to_date) for stat in statistics_class_list
                            if requirements_satisfied(stat, format_str)]
            
            ### REMEMBER THAT DATES IN FILE ARE FROM MOST RECENT TO OLDEST
            offsets = fill_offsets(file)
            stop_idx = FirstNotSmaller(from_date, offsets, file, pattern)
            start_idx = LastNotGreater(to_date, offsets, file, pattern)
            file.seek(offsets[start_idx])
            number_of_lines = stop_idx - start_idx

            for i, line in enumerate(file):
                if i > number_of_lines:
                    break
                match = pattern.match(line)
                if match is None:
                    print(f"couldn't match log format in line {i+start_idx}")
                    continue
                for stat in statistics_list:
                    stat.update_stats(match)

    except FileNotFoundError:
        print("no such file or directory")
        exit(1)
    for stat in statistics_list:
        print(stat)

