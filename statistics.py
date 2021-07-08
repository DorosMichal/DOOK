from abc import ABC, abstractmethod
from config import strip_str

def proper_units(size):
    if size >= 10**9:
        return f'{size/(10**9):2.f} GB'
    elif size >= 10**6:
        return f'{size/(10**6):2.f} MB'
    elif size >= 10**3:
        return f'{size/(10**3):2.f} KB'
    return f'{size} B'


class Statistic(ABC):
    requirements = []
    @abstractmethod
    def update_stats(self, matchobj):
        pass

    @abstractmethod
    def give_answer(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class RequestsNumber(Statistic):
    requirements = []
    def __init__(self, from, to):
        self.ctr = 0
        
    def update_stats(self, matchobj):
        self.ctr += 1
    
    def give_answer(self):
        return self.ctr

    def __repr__(self):
        return f"requests: {self.give_answer()}"


class RequestsPerSec(Statistic):
    requirements = []
    def __init__(self, from_date, to_date):
        self.no_of_seconds = (to_date-from_date).seconds
        self.ctr = 0
        
    def update_stats(self, matchobj):
        self.ctr += 1

    def give_answer(self):
        return self.ctr/self.no_of_seconds
        
    def __repr__(self):
        return f"requests/sec: {self.give_answer():.2f}"

class Responses(Statistic):
    requirements = ['s']
    def __init__(self, from_date, to_date):
        self.resp = dict()
        
    def update_stats(self, matchobj):
        code = int(matchobj.group('s').strip(strip_str))
        self.resp[code] = self.resp[code] + 1 if code in self.resp else 0

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
        code = matchobj.group('s').strip(strip_str)
        if code[0] == '2':
            length = matchobj.group('b').strip(strip_str)
            if length != '-':
                self.ctr += 1
                self.length_sum += int(length)

    def give_answer(self):
        return self.length_sum / self.ctr
        
    def __repr__(self):
        answer = proper_units(self.give_answer())
        return f"Avg size of 2xx responses: {answer}"
