from datetime import datetime


class VNAEvent:
    def __init__(self, func, repeat=0, timeEnd=datetime.now(), priority=0, title=""):
        self.title=title
        self.repeat = repeat
        self.timeEnd = timeEnd
        self.func = func
        self.priority = priority

    def inProcess(self):
        if self.timeEnd > datetime.now():
            return True
        if self.repeat:
            self.repeat -= 1
            return True
        return False

    def __lt__(self, other):
        return self.priority < other.priority
