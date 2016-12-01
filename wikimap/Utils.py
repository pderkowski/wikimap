import logging
import sys
import os
import subprocess
import ast
import cPickle
import urllib
import time
import itertools
import operator

def openOrExit(file, mode='r'):
    logger = logging.getLogger(__name__)

    if mode == 'r' and not os.path.isfile(file):
        logger.error('File {} does not exist.'.format(file))
        sys.exit()
    else:
        return open(file, mode)

def getProgName(fileName):
    return os.path.splitext(os.path.basename(fileName))[0]

def formatDuration(secs):
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

def configLogging():
    logging.basicConfig(format='%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s', datefmt='%H:%M:%S', level=logging.INFO)

def getParentDirectory(file):
    return os.path.join(os.path.dirname(os.path.abspath(file)), '..')

class ProgressBar(object):
    def __init__(self, name):
        self.name = name

    def report(self, count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)

        if count*blockSize > totalSize:
            sys.stdout.write("\33[2K\r" + self.name + "...DONE\n")
        else:
            sys.stdout.write("\33[2K\r" + self.name + "...%d%%" % percent)
        sys.stdout.flush()

class DumbProgressBar(object):
    def __init__(self):
        self.ticks = 0
        self.lastTickTime = time.time()

    def report(self):
        now = time.time()
        if (now - self.lastTickTime > 0.5): # prevent the progress bar from updating too frequently
            sys.stdout.write("\33[2K\rProcessing"+"."*self.ticks)
            sys.stdout.flush()
            self.lastTickTime = now
            self.ticks = (self.ticks + 1) % 4

    def cleanup(self):
        sys.stdout.write("\33[2K\r")
        sys.stdout.flush()

def call(command):
    logger = logging.getLogger(__name__)
    logger.info('Running command: {}'.format(command))
    subprocess.call(command, shell=True)

def loadFromFile(path):
    with open(path, 'r') as f:
        return ast.literal_eval(f.read()) # literal_eval only evaluates basic types instead of arbitrary code

def saveToFile(path, dict_):
    with open(path, 'w') as f:
        f.write(str(dict_))

def listToBinary(lst):
    return cPickle.dumps(lst, -1)

def download(url):
    return lambda output: urllib.urlretrieve(url, output, reporthook=ProgressBar(url).report)

def any2unicode(sth, encoding='utf8', errors='strict'):
    if isinstance(sth, unicode):
        return sth
    elif isinstance(sth, basestring):
        return unicode(sth, encoding, errors=errors)
    else:
        return unicode(str(sth), encoding, errors=errors)

def pipe(arg, *funcs):
    for f in funcs:
        arg = f(arg)
    return arg

class Logger(object):
    def __init__(self, iterator, frequency):
        self._iterator = iterator
        self._frequency = frequency

    def __iter__(self):
        logger = logging.getLogger(__name__)
        for (i, e) in enumerate(self._iterator):
            if self._frequency > 0 and i % self._frequency == 0:
                logger.info('Processed {} records'.format(i))
            yield e

def LogIt(frequency):
    return lambda iterator, frequency=frequency: Logger(iterator, frequency)

class GroupIt(object):
    def __init__(self, iterator):
        self._iterator = iterator

    def __iter__(self):
        for k, group in itertools.groupby(self._iterator, operator.itemgetter(0)):
            yield [k] + [p[1] for p in group]

def JoinIt(iterator):
    return itertools.imap(lambda e: u' '.join(e)+u'\n', iterator)

class DeferIt(object):
    def __init__(self, iteratorFactory):
        self._iteratorFactory = iteratorFactory

    def __iter__(self):
        return self._iteratorFactory()

def StringifyIt(iterator):
    return itertools.imap(lambda e: map(any2unicode, e), iterator)

def ColumnIt(columnNo):
    return lambda iterator, columnNo=columnNo: itertools.imap(operator.itemgetter(columnNo), iterator)

