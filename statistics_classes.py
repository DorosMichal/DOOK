from abc import ABC, abstractmethod
strip_str = '[]"' #used to strip matched group, potentially there could be other brackets etc.

def proper_units(size):
    if size is None:
        return None
    if size >= 10**9:
        return f'{size/(10**9):.2f} GB'
    if size >= 10**6:
        return f'{size/(10**6):.2f} MB'
    if size >= 10**3:
        return f'{size/(10**3):.2f} KB'
    return f'{size:.2f} B'


class Statistic(ABC):
    requirements = []

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def update_stats(self, matchobj):
        pass

    @abstractmethod
    def give_answer(self):
        pass


class RequestsNumber(Statistic):
    requirements = []

    def __init__(self, from_date, to_date):
        self.ctr = 0
        
    def update_stats(self, matchobj):
        self.ctr += 1
    
    def give_answer(self):
        return self.ctr

    def __repr__(self):
        return f"requests: {self.give_answer()}"


class RequestsPerSec(Statistic):
    requirements = ['t']

    def __init__(self, from_date, to_date):
        self.no_of_seconds = (to_date-from_date).total_seconds()
        self.ctr = 0
        
    def update_stats(self, matchobj):
        self.ctr += 1

    def give_answer(self): ##bledy dzielenia do obsluzenia
        try:
            return self.ctr/self.no_of_seconds
        except ZeroDivisionError:
            print("Date of start and end must be different to calculate RequestsPerSec")
            return None
        
    def __repr__(self):
        answer = self.give_answer()
        return "requests/sec: " + (f"{answer:.2f}" if answer else '---')

class Responses(Statistic):
    requirements = ['s']
    def __init__(self, from_date, to_date):
        self.resp = dict()
        
    def update_stats(self, matchobj):
        code = int(matchobj['s'].strip(strip_str))
        self.resp[code] = self.resp[code] + 1 if code in self.resp else 1

    def give_answer(self):
        return self.resp
        
    def __repr__(self):
        return f"responses: {self.give_answer()}"

class AvgSizeOf2xx(Statistic):
    requirements = ['s', 'b']
    def __init__(self, from_date, to_date):
        self.ctr = 0
        self.length_sum = 0
        
    def update_stats(self, matchobj):
        code = matchobj['s'].strip(strip_str)
        if code[0] == '2':
            length = matchobj['b'].strip(strip_str)
            if length != '-':
                self.ctr += 1
                self.length_sum += int(length)

    def give_answer(self):
        try:
            return self.length_sum / self.ctr
        except ZeroDivisionError:
            print("No 2xx response code found")
            return 0
        
    def __repr__(self):
        answer = proper_units(self.give_answer())
        return f"Avg size of 2xx responses: {answer}"
