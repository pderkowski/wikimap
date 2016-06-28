import logging
import sys
import os
import time

class Timer(object):
    def __init__(self, name='Timer'):
        self._name = name

    def start(self):
        self._start = time.time()

    def stop(self):
        logger = logging.getLogger(__name__)

        if not self._start:
            logger.warning('Timer not started!')
        self._end = time.time()

    def duration(self):
        logger = logging.getLogger(__name__)

        if self._start and self._end:
            return self._end - self._start
        else:
            logger.warning('Getting value of a timer that was not started or stopped.')

    def __str__(self):
        return '{} duration: {:.3f}'.format(self._name, self.duration())

def openOrExit(file, mode='r'):
    logger = logging.getLogger(__name__)

    if mode == 'r' and not os.path.isfile(file):
        logger.error('File does not exist.')
        sys.exit()
    else:
        return open(file, mode)

def getProgName(fileName):
    return os.path.splitext(os.path.basename(fileName))[0]

# def getLogger(fileName):
#     logger = logging.getLogger(getProgName(fileName))
#     logger.setLevel(logging.INFO)
#     handler = logging.StreamHandler()
#     handler.setLevel(logging.INFO)
#     formatter = logging.Formatter('%(asctime)s : %(module)s : %(levelname)s : %(message)s', "%H:%M:%S")
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     return logger

def configLogging():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
