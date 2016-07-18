import logging
import sys
import os

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