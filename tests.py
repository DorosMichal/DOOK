import pytest
from datetime import datetime
from statistics_classes import RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx
import re
import main
import statistics_classes as sc

@pytest.mark.re
def test_format_str_to_re_conversion():
    format_str = '%(u)s "random tekst"%(t)s "%(r)s"'
    proper_regex =  '(?P<u>(\\[.+?\\])|(\\".+?\\")|\\S+) \\"random tekst\\"(?P<t>(\\[.+?\\])|(\\".+?\\")|\\S+) (?P<r>(\\[.+?\\])|(\\".+?\\")|\\S+)'
    log = '- "random tekst"[01/Dec/2019:11:06:07 +0100] "GET /internal/user/5fe5aeac-261d-4e2f-9811-c054edda14fa/agenda/2019-12-01/2019-12-02 HTTP/1.1"'
    proper_match = re.match(proper_regex, log)
    
    test_regex = main.format_str_to_re(format_str)
    print(test_regex)
    test_match = re.match(test_regex, log)

    assert test_match is not None
    assert proper_match.group() == test_match.group()
    try:
        assert proper_match['r'] == test_match['r']
        assert proper_match['t'] == test_match['t']
    except KeyError as exc:
        assert False, f"didn't match 'r' group, ended with {exc} exception"

@pytest.fixture
def log():
    return 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]: 172.16.3.14 - - [01/Dec/2019:11:06:03 +0100] "GET /internal/user/03144bdb-805e-4a56-836f-3324a812fe0f/agenda/2019-12-01/2019-12-02 HTTP/1.1" 200 720 "-" "python-requests/2.22.0" 135485'

@pytest.fixture
def format_str():
    return '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

@pytest.fixture
def pattern(format_str):
    return main.prepare_pattern(format_str)

@pytest.fixture
def statistics_class_list():
    return [RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx]

@pytest.mark.re
def test_match(pattern, log):
    match = pattern.match(log)
    assert match is not None
    try:
        assert match['h'] == '172.16.3.14'
        assert match['D'] == '135485'
        assert match['s'] == '200'
        assert match['t'] == '[01/Dec/2019:11:06:03 +0100]'
        assert match['r'] == '"GET /internal/user/03144bdb-805e-4a56-836f-3324a812fe0f/agenda/2019-12-01/2019-12-02 HTTP/1.1"'
    except KeyError as exc:
        assert False, f"didn't match one of groups, ended with {exc} exception"

@pytest.mark.date
def test_date_from_match(pattern, log):
    match = pattern.match(log)
    date = main.get_date_from_match(match)

    assert date == datetime(2019,12,1,11,6,3)

@pytest.mark.date
def test_date_from_file(pattern):
    with open('test.txt') as file:
        next(file)
        date = main.get_date_from_file(file, 1, pattern)
        assert date == datetime(2019,12,1,11,6,4)
        date = main.get_date_from_file(file, 0, pattern)
        assert date == datetime(2019,12,1,11,6,5)

@pytest.mark.date
def test_correct_date__from_file_wins(pattern):
    from_date_str = "01-12-2019_10-03-50"
    to_date_str = "01-12-2019_13-03-50"
    with open('test.txt') as file:
        next(file)
        date = main.get_correct_date(from_date_str, 1, file, pattern)
        assert date == datetime(2019,12,1,11,6,4)
        date = main.get_correct_date(to_date_str, 0, file, pattern)
        assert date == datetime(2019,12,1,11,6,5)

@pytest.mark.date
def test_correct_date__from_user_wins(pattern):
    from_date_str = "01-12-2019_11-06-05"
    to_date_str = "01-12-2019_11-06-04"
    with open('test.txt') as file:
        next(file)
        date = main.get_correct_date(from_date_str, 1, file, pattern)
        assert date == datetime(2019,12,1,11,6,5)
        date = main.get_correct_date(to_date_str, 0, file, pattern)
        assert date == datetime(2019,12,1,11,6,4)

@pytest.mark.stats
def test_proper_units():
    assert sc.proper_units(None) is None
    assert sc.proper_units(2130 * 10**6) == "2.13 GB"
    assert sc.proper_units(43.01 * 10**6) == "43.01 MB"
    assert sc.proper_units(4321) == "4.32 KB"
    assert sc.proper_units(435.456) == "435.46 B"

@pytest.mark.stats
def test_main_no_dates(capsys, format_str, statistics_class_list):
    main.main('test.txt', None, None, format_str, statistics_class_list)
    out, err = capsys.readouterr()
    proper_output = """requests: 4
requests/sec: 4.00
responses: {200: 2, 300: 1, 204: 1}
Avg size of 2xx responses: 880.00 B
"""
    assert out == proper_output
    assert err == ''

@pytest.mark.stats
def test_main_to_date(capsys, format_str, statistics_class_list):
    main.main('test.txt', None, "01-12-2019_11-06-04", format_str, statistics_class_list)
    out, err = capsys.readouterr()
    proper_output = """requests: 3
Date of start and end must be different to calculate RequestsPerSec
requests/sec: ---
responses: {300: 1, 204: 1, 200: 1}
Avg size of 2xx responses: 960.00 B
"""
    assert out == proper_output
    assert err == ''

@pytest.mark.stats
def test_main_from_date(capsys, format_str, statistics_class_list):
    main.main('test.txt', "01-12-2019_11-06-05", None , format_str, statistics_class_list)
    out, err = capsys.readouterr()
    proper_output = """requests: 1
Date of start and end must be different to calculate RequestsPerSec
requests/sec: ---
responses: {200: 1}
Avg size of 2xx responses: 720.00 B
"""
    assert out == proper_output
    assert err == ''