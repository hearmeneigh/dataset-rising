import time
from halo import Halo


class Progress:
    def __init__(self, title: str, units: str):
        self.title = title
        self.units = units

        self.start = time.time()
        self.count = 0

        self.bar = Halo(text=title, spinner='dots4')
        self.bar.start()

    def update(self, completed: int = None, message: str = None):
        self.count += 1

        if self.count % 100 == 0:
            now = time.time()
            delta = now - self.start
            rate = round(self.count / delta, 2)
            self.bar.text = f'{self.title}: {self.count} [{rate} {self.units}/s]'

    def succeed(self, message: str):
        self.bar.succeed(message)

    def fail(self, message: str):
        self.bar.fail(message)
