import logging
import sys
import os
import subprocess
import ast
import cPickle
import urllib
import operator
import numpy
from itertools import imap, groupby

def openOrExit(file_, mode='r'):
    logger = logging.getLogger(__name__)

    if mode == 'r' and not os.path.isfile(file_):
        logger.error('File {} does not exist.'.format(file_))
        sys.exit()
    else:
        return open(file_, mode)

def getProgName(fileName):
    return os.path.splitext(os.path.basename(fileName))[0]

def formatDuration(secs):
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

def configLogging():
    logging.basicConfig(format='%(asctime)s:%(name)s:%(lineno)s:%(levelname)s:%(message)s', datefmt='%H:%M:%S', level=logging.INFO)

def getParentDirectory(file_):
    return os.path.join(os.path.dirname(os.path.abspath(file_)), '..')

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
        if arg is None:
            print f
    return arg

class PrintIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        def printAndReturn(sth):
            print repr(sth)
            return sth

        return imap(printAndReturn, self.iterator)

class LogIt(object):
    def __init__(self, frequency):
        self.frequency = frequency
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        logger = logging.getLogger(__name__)
        for (i, e) in enumerate(self.iterator):
            if self.frequency > 0 and i % self.frequency == 0:
                logger.info('Processed {} records'.format(i))
            yield e

class GroupIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        def join(arg):
            k, group = arg
            return [k] + [p[1] for p in group]

        return imap(join, groupby(self.iterator, operator.itemgetter(0)))

class JoinIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda e: u' '.join(e)+u'\n', self.iterator)

class DeferIt(object):
    def __init__(self, iteratorFactory):
        self.iteratorFactory = iteratorFactory

    def __iter__(self):
        return iter(self.iteratorFactory())

class StringifyIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda e: map(any2unicode, e), self.iterator)

class ColumnIt(object):
    def __init__(self, *columns):
        self.columns = columns
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return imap(operator.itemgetter(*self.columns), self.iterator)

class UnconsIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda lst: (lst[0], lst[1:]), self.iterator)

def any2array(something):
    if isinstance(something, numpy.ndarray):
        return something
    elif isinstance(something, list):
        return numpy.array(something)
    elif hasattr(something, "__iter__"):
        return numpy.array(list(something))
    else:
        raise ValueError("Argument is not convertable to an array.")
