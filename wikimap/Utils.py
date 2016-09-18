import logging
import sys
import os
import subprocess
import ast

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
        self.ticks = 1

    def report(self):
        sys.stdout.write("\33[2K\rProcessing"+"."*self.ticks)
        sys.stdout.flush()
        self.ticks = (self.ticks % 3) + 1

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