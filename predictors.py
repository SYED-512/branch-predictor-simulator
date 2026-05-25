class StaticPredictor:
    def __init__(self, always_taken=True):
        self.always_taken = always_taken
        self.name = f"Static ({'Taken' if always_taken else 'Not-Taken'})"
        self.correct = 0
        self.total = 0
    def predict(self, address):
        return self.always_taken
    def update(self, address, actual_taken):
        self.total += 1
        if self.predict(address) == actual_taken:
            self.correct += 1
    def accuracy(self):
        return (self.correct / self.total * 100) if self.total > 0 else 0

class OneBitPredictor:
    def __init__(self, table_size=256):
        self.table = {}
        self.table_size = table_size
        self.name = '1-Bit Predictor'
        self.correct = 0
        self.total = 0
    def _key(self, address):
        return address % self.table_size
    def predict(self, address):
        return self.table.get(self._key(address), True)
    def update(self, address, actual_taken):
        prediction = self.predict(address)
        self.total += 1
        if prediction == actual_taken:
            self.correct += 1
        self.table[self._key(address)] = actual_taken
    def accuracy(self):
        return (self.correct / self.total * 100) if self.total > 0 else 0

class TwoBitPredictor:
    def __init__(self, table_size=256):
        self.table = {}
        self.table_size = table_size
        self.name = '2-Bit Saturating Counter'
        self.correct = 0
        self.total = 0
    def _key(self, address):
        return address % self.table_size
    def predict(self, address):
        state = self.table.get(self._key(address), 2)
        return state >= 2
    def update(self, address, actual_taken):
        prediction = self.predict(address)
        self.total += 1
        if prediction == actual_taken:
            self.correct += 1
        key = self._key(address)
        state = self.table.get(key, 2)
        if actual_taken:
            self.table[key] = min(3, state + 1)
        else:
            self.table[key] = max(0, state - 1)
    def accuracy(self):
        return (self.correct / self.total * 100) if self.total > 0 else 0

class TournamentPredictor:
    def __init__(self, table_size=256, global_history_len=8):
        self.table_size = table_size
        self.gh_len = global_history_len
        self.global_history = 0
        self.gh_mask = (1 << global_history_len) - 1
        self.local_table = [2] * table_size
        self.global_table = [2] * (1 << global_history_len)
        self.selector = [2] * (1 << global_history_len)
        self.name = 'Tournament Predictor'
        self.correct = 0
        self.total = 0
    def _local_predict(self, address):
        return self.local_table[address % self.table_size] >= 2
    def _global_predict(self):
        return self.global_table[self.global_history] >= 2
    def predict(self, address):
        use_global = self.selector[self.global_history] >= 2
        return self._global_predict() if use_global else self._local_predict(address)
    def update(self, address, actual_taken):
        prediction = self.predict(address)
        self.total += 1
        if prediction == actual_taken:
            self.correct += 1
        local_correct = self._local_predict(address) == actual_taken
        global_correct = self._global_predict() == actual_taken
        gh = self.global_history
        if global_correct and not local_correct:
            self.selector[gh] = min(3, self.selector[gh] + 1)
        elif local_correct and not global_correct:
            self.selector[gh] = max(0, self.selector[gh] - 1)
        lk = address % self.table_size
        if actual_taken:
            self.local_table[lk] = min(3, self.local_table[lk] + 1)
        else:
            self.local_table[lk] = max(0, self.local_table[lk] - 1)
        if actual_taken:
            self.global_table[gh] = min(3, self.global_table[gh] + 1)
        else:
            self.global_table[gh] = max(0, self.global_table[gh] - 1)
        self.global_history = ((self.global_history << 1) | int(actual_taken)) & self.gh_mask
    def accuracy(self):
        return (self.correct / self.total * 100) if self.total > 0 else 0
