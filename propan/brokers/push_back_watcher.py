from collections import Counter


class PushBackWatcher:
    memory = Counter()
    max_tries: int

    def __init__(self, max_tries: int = 3):
        self.max_tries = max_tries

    def add(self, message: str):
        self.memory[message] += 1

    def is_max(self, message: str):
        return self.memory[message] > self.max_tries

    def remove(self, message: str):
        self.memory[message] = 0
        self.memory += Counter()
