import time
import sys
import pickle
import struct

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

def list2bytes(lst):
    return pickle.dumps(lst, 2)

def bytes2list(bytes_):
    return pickle.loads(bytes_)

class TrivialConverter(object):
    def encode(self, value):
        return str(value)

    def decode(self, value):
        return value

class IntConverter(object):
    def __init__(self):
        self.size = 4

    def encode(self, value):
        return struct.pack("<i", value)

    def decode(self, string):
        return struct.unpack("<i", string)[0]

class FloatConverter(object):
    def __init__(self):
        self.size = 8

    def encode(self, value):
        return struct.pack("<d", value)

    def decode(self, string):
        return struct.unpack("<d", string)[0]

class ListConverter(object):
    def __init__(self, converter):
        self._converter = converter

    def encode(self, lst):
        bytes_ = ''.join(map(self._converter.encode, lst))
        return str(bytes_)

    def decode(self, string):
        codes = [string[i:i+self._converter.size] for i in range(0, len(string), self._converter.size)]
        return map(self._converter.decode, codes)
