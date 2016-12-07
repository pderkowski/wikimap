import time
import sys

class DumbProgressBar(object):
    def __init__(self):
        self.ticks = 0
        self.lastTickTime = time.time()

    def report(self):
        now = time.time()
        if now - self.lastTickTime > 0.5: # prevent the progress bar from updating too frequently
            sys.stdout.write("\33[2K\rProcessing"+"."*self.ticks)
            sys.stdout.flush()
            self.lastTickTime = now
            self.ticks = (self.ticks + 1) % 4

    def cleanup(self):
        sys.stdout.write("\33[2K\r")
        sys.stdout.flush()
